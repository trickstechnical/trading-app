from decimal import Decimal

from app.models import PaperTrade


ZERO = Decimal("0")


def calculate_metrics(account_id: int = 1) -> dict:
    trades = (
        PaperTrade.query
        .filter_by(account_id=account_id)
        .order_by(PaperTrade.created_at.asc(), PaperTrade.id.asc())
        .all()
    )

    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "net_pnl": 0.0,
            "profit_factor": None,
            "average_win": 0.0,
            "average_loss": 0.0,
            "max_drawdown": 0.0,
        }

    winning_trades = [
        trade for trade in trades
        if Decimal(str(trade.realized_pnl)) > ZERO
    ]

    losing_trades = [
        trade for trade in trades
        if Decimal(str(trade.realized_pnl)) < ZERO
    ]

    pnl_values = [
        Decimal(str(trade.realized_pnl))
        for trade in trades
    ]

    total_trades = len(trades)
    winning_count = len(winning_trades)
    losing_count = len(losing_trades)

    gross_profit = sum(
        (Decimal(str(trade.realized_pnl)) for trade in winning_trades),
        ZERO,
    )

    gross_loss = abs(
        sum(
            (Decimal(str(trade.realized_pnl)) for trade in losing_trades),
            ZERO,
        )
    )

    net_pnl = sum(pnl_values, ZERO)

    win_rate = (
        Decimal(winning_count) / Decimal(total_trades) * 100
    )

    average_win = (
        gross_profit / Decimal(winning_count)
        if winning_count
        else ZERO
    )

    average_loss = (
        gross_loss / Decimal(losing_count)
        if losing_count
        else ZERO
    )

    profit_factor = (
        float(gross_profit / gross_loss)
        if gross_loss > ZERO
        else None
    )

    # Calculate maximum drawdown from cumulative realized P&L.
    cumulative_pnl = ZERO
    peak_pnl = ZERO
    max_drawdown = ZERO

    for pnl in pnl_values:
        cumulative_pnl += pnl
        peak_pnl = max(peak_pnl, cumulative_pnl)

        drawdown = peak_pnl - cumulative_pnl
        max_drawdown = max(max_drawdown, drawdown)

    return {
        "total_trades": total_trades,
        "winning_trades": winning_count,
        "losing_trades": losing_count,
        "win_rate": round(float(win_rate), 2),
        "gross_profit": round(float(gross_profit), 2),
        "gross_loss": round(float(gross_loss), 2),
        "net_pnl": round(float(net_pnl), 2),
        "profit_factor": (
            round(profit_factor, 2)
            if isinstance(profit_factor, (float, int))
            else None
        ),
        "average_win": round(float(average_win), 2),
        "average_loss": round(float(average_loss), 2),
        "max_drawdown": round(float(max_drawdown), 2),
    }