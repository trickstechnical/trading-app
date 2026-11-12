from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import desc

from app.extensions import db
from app.models import (
    Candle,
    PaperAccount,
    PaperOrder,
    PaperPosition,
    PaperTrade,
)

from app.paper_trading.charges import calculate_equity_delivery_charges
from app.paper_trading.execution import get_exit_price

CANDLE_INTERVAL = "5m"
CANDLE_DURATION = timedelta(minutes=5)


def monitor_positions() -> list[dict]:
    try:
        account = (
            PaperAccount.query
            .filter_by(id=1)
            .with_for_update()
            .first()
        )

        if account is None:
            raise ValueError("Paper account not initialized")

        positions = (
            PaperPosition.query
            .filter_by(account_id=1)
            .with_for_update()
            .all()
        )

        results = []
        now = datetime.now(timezone.utc)

        for position in positions:
            candle = (
                Candle.query
                .filter_by(
                    instrument_id=position.instrument_id,
                    interval=CANDLE_INTERVAL,
                )
                .order_by(desc(Candle.timestamp))
                .first()
            )

            if candle is None:
                continue

            timestamp = candle.timestamp

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

            if timestamp + CANDLE_DURATION > now:
                continue

            exit_result = get_exit_price(
                candle_open=Decimal(str(candle.open)),
                candle_high=Decimal(str(candle.high)),
                candle_low=Decimal(str(candle.low)),
                stop_loss=Decimal(str(position.stop_loss)),
                target_price=Decimal(str(position.target_price)),
            )

            if exit_result is None:
                continue

            exit_price, exit_reason = exit_result

            quantity = position.quantity
            entry_price = Decimal(str(position.average_price))

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
                - entry_price * quantity
            )

            net_pnl = (
                gross_pnl
                - allocated_entry_charges
                - sell_charges
            )

            order = PaperOrder(
                account_id=account.id,
                instrument_id=position.instrument_id,
                side="SELL",
                quantity=quantity,
                price=exit_price,
                total_value=sell_value,
                charges=sell_charges,
                status="FILLED",
                order_type="STOP" if exit_reason == "STOP_LOSS" else "TARGET",
            )

            db.session.add(order)
            db.session.flush()

            trade = PaperTrade(
                account_id=account.id,
                instrument_id=position.instrument_id,
                order_id=order.id,
                quantity=quantity,
                entry_price=entry_price,
                exit_price=exit_price,
                entry_charges=allocated_entry_charges,
                exit_charges=sell_charges,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                realized_pnl=net_pnl,
                exit_reason=exit_reason,
            )
            db.session.add(trade)

            results.append({
                "instrument_id": position.instrument_id,
                "quantity": quantity,
                "exit_price": float(exit_price),
                "gross_pnl": float(gross_pnl),
                "net_pnl": float(net_pnl),
                "realized_pnl": float(net_pnl),
                "exit_reason": exit_reason,
            })

            db.session.delete(position)

        db.session.commit()
        return results

    except Exception:
        db.session.rollback()
        raise