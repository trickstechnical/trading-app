from datetime import datetime, timezone
from math import isfinite

def validate_candle(candle: dict) -> dict:
    required = ("timestamp", "open", "high", "low", "close", "volume")
    missing = [key for key in required if key not in candle]
    if missing:
        raise ValueError(f"Missing candle fields: {', '.join(missing)}")

    ts = candle["timestamp"]
    if isinstance(ts, (int, float)):
        ts = datetime.fromtimestamp(ts, tz=timezone.utc)
    elif isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        ts = ts.replace(tzinfo=ts.tzinfo or timezone.utc).astimezone(timezone.utc)
    elif isinstance(ts, datetime):
        ts = ts.replace(tzinfo=ts.tzinfo or timezone.utc).astimezone(timezone.utc)
    else:
        raise ValueError("Invalid candle timestamp")

    values = {}
    for key in ("open", "high", "low", "close", "volume"):
        try:
            value = float(candle[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {key}") from exc
        if not isfinite(value):
            raise ValueError(f"{key} must be finite")
        values[key] = value

    prices = [values[k] for k in ("open", "high", "low", "close")]
    if min(prices) <= 0:
        raise ValueError("OHLC prices must be greater than zero")
    if values["high"] < max(prices) or values["low"] > min(prices):
        raise ValueError("Invalid candle high/low range")
    if values["volume"] < 0:
        raise ValueError("Volume cannot be negative")
    return {"timestamp": ts, **values}

def validate_candles(candles: list[dict]) -> list[dict]:
    by_timestamp = {}
    for candle in candles:
        item = validate_candle(candle)
        by_timestamp[item["timestamp"]] = item
    return [by_timestamp[key] for key in sorted(by_timestamp)]