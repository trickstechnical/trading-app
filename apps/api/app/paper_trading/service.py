from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import desc

from app.extensions import db
from app.models import (
    Candle,
    Instrument,
    PaperAccount,
    PaperOrder,
    PaperPosition,
    PaperTrade,
)

from app.paper_trading.charges import (
    calculate_equity_delivery_charges,
)

STARTING_BALANCE = Decimal("100000.00")
CANDLE_INTERVAL = "5m"
CANDLE_DURATION = timedelta(minutes=5)

# The index is deliberately excluded. Add actual tradable instruments later.
TRADABLE_SYMBOLS = {"NSE:SBIN-EQ"}

ATR_PERIOD = 14
STOP_LOSS_MULTIPLIER = Decimal("1.5")
RISK_REWARD_RATIO = Decimal("2")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_latest_completed_candle(instrument_id: int):
    now = datetime.now(timezone.utc)

    candles = (
        Candle.query
        .filter_by(
            instrument_id=instrument_id,
            interval=CANDLE_INTERVAL,
        )
        .order_by(desc(Candle.timestamp))
        .limit(1)
        .all()
    )

    if not candles:
        raise ValueError("No market candles are available")

    candle = candles[0]
    timestamp = candle.timestamp

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)

    if timestamp + CANDLE_DURATION > now:
        raise ValueError("The latest candle is not completed yet")

    return candle


def calculate_atr_for_instrument(instrument_id: int) -> Decimal:
    candles = (
        Candle.query
        .filter_by(
            instrument_id=instrument_id,
            interval=CANDLE_INTERVAL,
        )
        .order_by(desc(Candle.timestamp))
        .limit(ATR_PERIOD + 1)
        .all()
    )

    candles.reverse()

    if len(candles) < ATR_PERIOD + 1:
        raise ValueError("Not enough candles to calculate ATR")

    true_ranges = []

    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]

        high = Decimal(str(current.high))
        low = Decimal(str(current.low))
        previous_close = Decimal(str(previous.close))

        true_range = max(
            high - low,
            abs(high - previous_close),
            abs(low - previous_close),
        )

        true_ranges.append(true_range)

    return sum(true_ranges[-ATR_PERIOD:]) / Decimal(ATR_PERIOD)


def get_account_for_update():
    account = (
        PaperAccount.query
        .filter_by(id=1)
        .with_for_update()
        .first()
    )

    if account is None:
        raise ValueError(
            "Paper account not initialized. Run flask init-paper-account."
        )

    return account


def execute_paper_order(
    symbol: str,
    side: str,
    quantity: int,
) -> dict:
    symbol = symbol.strip()
    side = side.upper()

    if symbol not in TRADABLE_SYMBOLS:
        raise ValueError("This instrument is not enabled for paper trading")

    if side not in {"BUY", "SELL"}:
        raise ValueError("Side must be BUY or SELL")

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive integer")

    try:
        account = get_account_for_update()

        instrument = Instrument.query.filter_by(symbol=symbol).first()

        if instrument is None:
            raise ValueError("Instrument not found")

        candle = get_latest_completed_candle(instrument.id)
        price = money(Decimal(str(candle.close)))
        total_value = money(price * quantity)

        position = (
            PaperPosition.query
            .filter_by(
                account_id=account.id,
                instrument_id=instrument.id,
            )
            .with_for_update()
            .first()
        )

        if side == "BUY":
            charges = calculate_equity_delivery_charges(
                price=price,
                quantity=quantity,
                side="BUY",
            )

            buy_charges = charges["total_charges"]
            order_value = price * quantity
            total_debit = order_value + buy_charges

            if account.balance < total_debit:
                raise ValueError("Insufficient virtual balance")

            atr = calculate_atr_for_instrument(instrument.id)
            risk_distance = atr * STOP_LOSS_MULTIPLIER

            if risk_distance <= 0:
                raise ValueError("Invalid ATR; cannot calculate risk levels")

            account.balance -= total_debit

            if position is None:
                position = PaperPosition(
                    account_id=account.id,
                    instrument_id=instrument.id,
                    quantity=quantity,
                    average_price=price,
                    stop_loss=money(price - risk_distance),
                    target_price=money(
                        price + risk_distance * RISK_REWARD_RATIO
                    ),
                    total_entry_value=order_value,
                    entry_charges=buy_charges,
                )
                position.total_entry_value = order_value
                position.entry_charges = buy_charges
                db.session.add(position)

            else:
                position.quantity += quantity
                position.total_entry_value += order_value
                position.entry_charges += buy_charges

                position.average_price = (
                    position.total_entry_value / position.quantity
                )

                # Recalculate protective levels using the new average entry.
                new_risk = atr * STOP_LOSS_MULTIPLIER
                new_average = Decimal(str(position.average_price))
                position.stop_loss = money(new_average - new_risk)
                position.target_price = money(
                    new_average + new_risk * RISK_REWARD_RATIO
                )

        else:
            if position is None or position.quantity < quantity:
                raise ValueError("Insufficient position quantity to sell")

            exit_price = price
            sell_charges = calculate_equity_delivery_charges(
                price=exit_price,
                quantity=quantity,
                side="SELL",
            )["total_charges"]

            sell_value = exit_price * quantity
            account.balance += sell_value - sell_charges

            allocated_entry_charges = (
                Decimal(str(position.entry_charges or 0))
                * Decimal(quantity)
                / Decimal(position.quantity)
            )

            gross_pnl = (
                sell_value
                - Decimal(str(position.average_price)) * quantity
            )

            net_pnl = (
                gross_pnl
                - allocated_entry_charges
                - sell_charges
            )

            order = PaperOrder(
                account_id=account.id,
                instrument_id=instrument.id,
                side=side,
                quantity=quantity,
                price=exit_price,
                total_value=sell_value,
                charges=sell_charges,
                status="FILLED",
                order_type="MARKET",
            )

            db.session.add(order)
            db.session.flush()

            trade = PaperTrade(
                account_id=account.id,
                instrument_id=instrument.id,
                order_id=order.id,
                quantity=quantity,
                entry_price=Decimal(str(position.average_price)),
                exit_price=exit_price,
                entry_charges=allocated_entry_charges,
                exit_charges=sell_charges,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                realized_pnl=net_pnl,
                exit_reason="MANUAL",
            )
            db.session.add(trade)

            position.quantity -= quantity
            remaining_quantity = position.quantity

            if remaining_quantity == 0:
                db.session.delete(position)
            else:
                position.entry_charges -= allocated_entry_charges
                if position.total_entry_value is not None:
                    position.total_entry_value -= Decimal(str(position.average_price)) * quantity

            # Save the SELL order and trade below without creating it twice.
            db.session.commit()

            return {
                "order_id": order.id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": float(exit_price),
                "total_value": float(sell_value),
                "gross_pnl": float(gross_pnl),
                "net_pnl": float(net_pnl),
                "realized_pnl": float(net_pnl),
                "remaining_quantity": remaining_quantity,
                "status": "FILLED",
            }

        order = PaperOrder(
            account_id=account.id,
            instrument_id=instrument.id,
            side=side,
            quantity=quantity,
            price=price,
            total_value=total_value,
            status="FILLED",
            order_type="MARKET",
        )
        order.charges = buy_charges

        db.session.add(order)
        db.session.commit()

        return {
            "order_id": order.id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": float(price),
            "total_value": float(total_value),
            "balance": float(account.balance),
            "status": "FILLED",
        }

    except Exception:
        db.session.rollback()
        raise