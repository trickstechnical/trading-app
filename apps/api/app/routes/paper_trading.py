from decimal import Decimal

from flask import Blueprint, jsonify, request

from app.models import (
    PaperAccount,
    PaperOrder,
    PaperPosition,
    PaperTrade,
)
from app.paper_trading.service import (
    execute_paper_order,
    get_latest_completed_candle,
)
from app.paper_trading.monitor import monitor_positions
from app.paper_trading.analytics import calculate_metrics
from app.paper_trading.dashboard import get_dashboard

paper_bp = Blueprint(
    "paper_trading",
    __name__,
    url_prefix="/api/paper",
)


@paper_bp.post("/orders")
def create_paper_order():
    data = request.get_json(silent=True) or {}

    symbol = data.get("symbol")
    side = data.get("side")
    quantity = data.get("quantity")

    if not symbol or not side or quantity is None:
        return jsonify({
            "error": "symbol, side and quantity are required",
        }), 400

    try:
        result = execute_paper_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
        )

        return jsonify(result), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@paper_bp.get("/portfolio")
def get_portfolio():
    account = PaperAccount.query.filter_by(id=1).first()

    if account is None:
        return jsonify({"error": "Paper account not initialized"}), 404

    positions = (
        PaperPosition.query
        .filter_by(account_id=account.id)
        .all()
    )

    position_results = []
    total_unrealized_pnl = Decimal("0.00")
    total_market_value = Decimal("0.00")

    for position in positions:
        try:
            candle = get_latest_completed_candle(position.instrument_id)
        except ValueError:
            continue

        current_price = Decimal(str(candle.close))
        average_price = Decimal(str(position.average_price))

        market_value = current_price * position.quantity
        unrealized_pnl = (
            current_price - average_price
        ) * position.quantity

        total_market_value += market_value
        total_unrealized_pnl += unrealized_pnl

        position_results.append({
            "symbol": position.instrument.symbol,
            "quantity": position.quantity,
            "average_price": float(average_price),
            "current_price": float(current_price),
            "market_value": float(market_value),
            "unrealized_pnl": float(unrealized_pnl),
            "stop_loss": (
                float(position.stop_loss)
                if position.stop_loss is not None else None
            ),
            "target_price": (
                float(position.target_price)
                if position.target_price is not None else None
            ),
        })

    realized_pnl = sum(
        (
            Decimal(str(trade.realized_pnl))
            for trade in PaperTrade.query.filter_by(
                account_id=account.id
            ).all()
        ),
        Decimal("0.00"),
    )

    equity = (
        Decimal(str(account.balance))
        + total_market_value
    )

    return jsonify({
        "initial_balance": float(account.initial_balance),
        "available_balance": float(account.balance),
        "market_value": float(total_market_value),
        "equity": float(equity),
        "realized_pnl": float(realized_pnl),
        "unrealized_pnl": float(total_unrealized_pnl),
        "total_pnl": float(realized_pnl + total_unrealized_pnl),
        "positions": position_results,
    })


@paper_bp.get("/orders")
def get_orders():
    account = PaperAccount.query.filter_by(id=1).first()

    if account is None:
        return jsonify({"error": "Paper account not initialized"}), 404

    orders = (
        PaperOrder.query
        .filter_by(account_id=account.id)
        .order_by(PaperOrder.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "orders": [
            {
                "id": order.id,
                "symbol": order.instrument.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "price": float(order.price),
                "total_value": float(order.total_value),
                "status": order.status,
                "order_type": order.order_type,
                "created_at": order.created_at.isoformat(),
            }
            for order in orders
        ]
    })


@paper_bp.get("/trades")
def get_trades():
    account = PaperAccount.query.filter_by(id=1).first()

    if account is None:
        return jsonify({"error": "Paper account not initialized"}), 404

    trades = (
        PaperTrade.query
        .filter_by(account_id=account.id)
        .order_by(PaperTrade.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "trades": [
            {
                "id": trade.id,
                "symbol": trade.instrument.symbol,
                "entry_price": float(trade.entry_price),
                "exit_price": float(trade.exit_price),
                "quantity": trade.quantity,
                "gross_pnl": float(trade.gross_pnl) if trade.gross_pnl is not None else float(trade.realized_pnl),
                "entry_charges": float(trade.entry_charges) if trade.entry_charges is not None else 0.0,
                "exit_charges": float(trade.exit_charges) if trade.exit_charges is not None else 0.0,
                "net_pnl": float(trade.net_pnl) if trade.net_pnl is not None else float(trade.realized_pnl),
                "realized_pnl": float(trade.realized_pnl),
                "exit_reason": trade.exit_reason,
                "created_at": trade.created_at.isoformat(),
            }
            for trade in trades
        ]
    })


@paper_bp.post("/monitor")
def run_position_monitor():
    try:
        results = monitor_positions()

        return jsonify({
            "message": "Position monitoring completed",
            "exits": results,
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

@paper_bp.get("/analytics")
def paper_analytics():
    result = calculate_metrics(account_id=1)

    return jsonify(result), 200

@paper_bp.get("/dashboard")
def paper_dashboard():
    try:
        result = get_dashboard(account_id=1)
        return jsonify(result), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404