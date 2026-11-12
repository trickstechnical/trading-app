from datetime import datetime
from zoneinfo import ZoneInfo

INDIA_TZ = ZoneInfo("Asia/Kolkata")


def calculate_ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise ValueError(f"At least {period} values are required")

    multiplier = 2 / (period + 1)

    ema = sum(values[:period]) / period

    for value in values[period:]:
        ema = (value * multiplier) + (ema * (1 - multiplier))

    return ema


def calculate_session_vwap(candles: list[dict]) -> float:
    if not candles:
        raise ValueError("Candles are required to calculate VWAP")

    latest_timestamp = candles[-1]["timestamp"]

    if latest_timestamp.tzinfo is None:
        latest_timestamp = latest_timestamp.replace(tzinfo=ZoneInfo("UTC"))

    latest_session = latest_timestamp.astimezone(INDIA_TZ).date()

    cumulative_price_volume = 0.0
    cumulative_volume = 0.0

    for candle in candles:
        timestamp = candle["timestamp"]

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))

        session_date = timestamp.astimezone(INDIA_TZ).date()

        if session_date != latest_session:
            continue

        typical_price = (
            candle["high"] + candle["low"] + candle["close"]
        ) / 3

        volume = candle["volume"]

        cumulative_price_volume += typical_price * volume
        cumulative_volume += volume

    if cumulative_volume == 0:
        raise ValueError("Cannot calculate VWAP with zero volume")

    return cumulative_price_volume / cumulative_volume


def calculate_atr(candles: list[dict], period: int = 14) -> float:
    if len(candles) < period + 1:
        raise ValueError(f"At least {period + 1} candles are required")

    true_ranges = []

    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]

        true_range = max(
            current["high"] - current["low"],
            abs(current["high"] - previous["close"]),
            abs(current["low"] - previous["close"]),
        )

        true_ranges.append(true_range)

    recent_ranges = true_ranges[-period:]

    return sum(recent_ranges) / period


def calculate_average_volume(
    candles: list[dict],
    period: int = 20,
) -> float:
    if len(candles) < period + 1:
        raise ValueError(f"At least {period + 1} candles are required")

    # Exclude the current candle from the average.
    previous_volumes = [
        candle["volume"]
        for candle in candles[-(period + 1):-1]
    ]

    return sum(previous_volumes) / period