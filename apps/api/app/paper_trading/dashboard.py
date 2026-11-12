from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models import (
    PaperAccount,
    PaperPosition,
    PaperOrder,
    PaperTrade,
    Candle,
    Instrument,
)

from app.paper_trading.analytics import calculate_metrics


ZERO = Decimal("0")


def serialize_decimal(value):
    return round(float(value or ZERO), 2)


def get_dashboard(account_id=1):
    account = PaperAccount.query.get(account_id)

    if not account:
        raise ValueError("Paper account not found")

    positions = PaperPosition.query.filter_by(
        account_id=account_id
    ).all()

    orders = (
        PaperOrder.query
        .filter_by(account_id=account_id)
        .order_by(PaperOrder.created_at.desc())
        .limit(10)
        .all()
    )

    trades = (
        PaperTrade.query
        .filter_by(account_id=account_id)
        .order_by(PaperTrade.created_at.desc())
        .limit(10)
        .all()
    )

    position_data = []

    market_value = ZERO
    unrealized_pnl = ZERO

    now = datetime.now(timezone.utc)
    candle_duration = timedelta(minutes=5)

    for position in positions:
        instrument = position.instrument

        candidates = (
            Candle.query
            .filter_by(
                instrument_id=position.instrument_id,
                interval="5m",
            )
            .order_by(Candle.timestamp.desc())
            .limit(10)
            .all()
        )

        latest_completed_candle = None
        for candle in candidates:
            timestamp = candle.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

            if timestamp + candle_duration <= now:
                latest_completed_candle = candle
                break

        current_price = (
            Decimal(str(latest_completed_candle.close))
            if latest_completed_candle
            else Decimal(str(position.average_price))
        )

        position_unrealized_pnl = (
            Decimal(str(current_price)) - Decimal(str(position.average_price))
        ) * Decimal(str(position.quantity))

        position_value = Decimal(str(current_price)) * Decimal(str(position.quantity))

        market_value += position_value
        unrealized_pnl += position_unrealized_pnl

        position_data.append({
            "symbol": instrument.symbol,
            "quantity": position.quantity,
            "average_price": serialize_decimal(position.average_price),
            "current_price": serialize_decimal(current_price),
            "market_value": serialize_decimal(position_value),
            "unrealized_pnl": serialize_decimal(position_unrealized_pnl),
            "stop_loss": serialize_decimal(position.stop_loss),
            "target_price": serialize_decimal(position.target_price),
        })

    realized_pnl = sum(
        (
            Decimal(str(trade.realized_pnl))
            for trade in PaperTrade.query.filter_by(
                account_id=account_id
            ).all()
        ),
        ZERO,
    )

    equity = Decimal(str(account.balance)) + market_value

    performance = calculate_metrics(account_id)

    initial_balance = Decimal(str(account.initial_balance))

    total_pnl = equity - initial_balance

    return_percentage = (
        (total_pnl / initial_balance) * Decimal("100")
        if initial_balance > ZERO
        else ZERO
    )

    all_trades = (
        PaperTrade.query
        .filter_by(account_id=account.id)
        .order_by(PaperTrade.created_at.asc(), PaperTrade.id.asc())
        .all()
    )

    running_equity = Decimal(str(account.initial_balance))
    equity_curve = [
        {
            "timestamp": account.created_at.isoformat(),
            "equity": float(running_equity),
        }
    ]

    pnl_history = []

    for trade in all_trades:
        net_pnl = Decimal(str(
            trade.net_pnl
            if trade.net_pnl is not None
            else trade.realized_pnl
        ))

        running_equity += net_pnl

        pnl_history.append({
            "timestamp": trade.created_at.isoformat(),
            "realized_pnl": float(net_pnl),
        })

        equity_curve.append({
            "timestamp": trade.created_at.isoformat(),
            "equity": float(running_equity),
        })

    now = datetime.now(timezone.utc)
    candle_duration = timedelta(minutes=5)

    sbin_instrument = Instrument.query.filter_by(
        symbol="NSE:SBIN-EQ"
    ).first()

    latest_candle = None

    if sbin_instrument:
        sbin_candidates = (
            Candle.query
            .filter_by(
                instrument_id=sbin_instrument.id,
                interval="5m",
            )
            .order_by(Candle.timestamp.desc())
            .limit(10)
            .all()
        )

        for candle in sbin_candidates:
            timestamp = candle.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

            if timestamp + candle_duration <= now:
                latest_candle = candle
                break

    market = {
        "symbol": "NSE:SBIN-EQ",
        "current_price": (
            serialize_decimal(latest_candle.close)
            if latest_candle
            else 0.0
        ),
    }

    return {
        "account": {
            "initial_balance": serialize_decimal(account.initial_balance),
            "available_balance": serialize_decimal(account.balance),
            "market_value": serialize_decimal(market_value),
            "equity": serialize_decimal(equity),
            "realized_pnl": serialize_decimal(realized_pnl),
            "unrealized_pnl": serialize_decimal(unrealized_pnl),
            "total_pnl": serialize_decimal(
                equity - Decimal(str(account.initial_balance))
            ),
            "return_percentage": round(float(return_percentage), 2),
        },
        "performance": performance,
        "positions": position_data,
        "recent_orders": [
            {
                "id": order.id,
                "symbol": order.instrument.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "price": serialize_decimal(order.price),
                "charges": serialize_decimal(order.charges),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
            }
            for order in orders
        ],
        "recent_trades": [
            {
                "id": trade.id,
                "symbol": trade.instrument.symbol,
                "quantity": trade.quantity,
                "entry_price": serialize_decimal(trade.entry_price),
                "exit_price": serialize_decimal(trade.exit_price),
                "gross_pnl": serialize_decimal(
                    trade.gross_pnl if trade.gross_pnl is not None else trade.realized_pnl
                ),
                "entry_charges": serialize_decimal(
                    trade.entry_charges if trade.entry_charges is not None else ZERO
                ),
                "exit_charges": serialize_decimal(
                    trade.exit_charges if trade.exit_charges is not None else ZERO
                ),
                "net_pnl": serialize_decimal(
                    trade.net_pnl if trade.net_pnl is not None else trade.realized_pnl
                ),
                "realized_pnl": serialize_decimal(trade.realized_pnl),
                "exit_reason": trade.exit_reason,
                "created_at": trade.created_at.isoformat(),
            }
            for trade in trades
        ],
        "equity_curve": equity_curve,
        "pnl_history": pnl_history,
        "market": market,
    }