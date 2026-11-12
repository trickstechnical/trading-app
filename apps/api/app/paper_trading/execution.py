from decimal import Decimal
from typing import Optional


def get_exit_price(
    candle_open: Decimal,
    candle_high: Decimal,
    candle_low: Decimal,
    stop_loss: Decimal,
    target_price: Decimal,
) -> Optional[tuple[Decimal, str]]:
    """
    Returns the simulated exit price and reason.

    Stop-loss takes priority if both stop-loss and target
    are reached in the same candle.
    """

    # Market gaps below stop-loss.
    if candle_open <= stop_loss:
        return candle_open, "STOP_LOSS"

    # Market gaps above target.
    if candle_open >= target_price:
        return target_price, "TARGET"

    # Both levels touched in the same candle.
    if candle_low <= stop_loss and candle_high >= target_price:
        return stop_loss, "STOP_LOSS"

    # Stop-loss touched.
    if candle_low <= stop_loss:
        return stop_loss, "STOP_LOSS"

    # Target touched.
    if candle_high >= target_price:
        return target_price, "TARGET"

    return None