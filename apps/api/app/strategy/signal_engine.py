from app.strategy.indicators import (
    calculate_atr,
    calculate_average_volume,
    calculate_ema,
    calculate_session_vwap,
)
from app.strategy.rules import calculate_scores

MINIMUM_CANDLES = 60
ATR_MULTIPLIER = 1.5
RISK_REWARD_RATIO = 2


def generate_signal(candles: list[dict]) -> dict:
    if len(candles) < MINIMUM_CANDLES:
        raise ValueError(
            f"At least {MINIMUM_CANDLES} completed candles are required"
        )

    closes = [candle["close"] for candle in candles]

    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    vwap = calculate_session_vwap(candles)
    atr = calculate_atr(candles, 14)
    average_volume = calculate_average_volume(candles, 20)

    result = calculate_scores(
        candles=candles,
        ema20=ema20,
        ema50=ema50,
        vwap=vwap,
        average_volume=average_volume,
    )

    entry_price = candles[-1]["close"]
    risk_distance = atr * ATR_MULTIPLIER

    stop_loss = None
    target_price = None

    if result["signal"] == "BUY":
        stop_loss = entry_price - risk_distance
        target_price = entry_price + (
            risk_distance * RISK_REWARD_RATIO
        )

    elif result["signal"] == "SELL":
        stop_loss = entry_price + risk_distance
        target_price = entry_price - (
            risk_distance * RISK_REWARD_RATIO
        )

    return {
        **result,
        "timestamp": candles[-1]["timestamp"].isoformat(),
        "entry_price": round(entry_price, 2),
        "stop_loss": (
            round(stop_loss, 2) if stop_loss is not None else None
        ),
        "target_price": (
            round(target_price, 2) if target_price is not None else None
        ),
        "risk_reward_ratio": RISK_REWARD_RATIO,
        "indicators": {
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2),
            "vwap": round(vwap, 2),
            "atr14": round(atr, 2),
            "average_volume_20": round(average_volume, 2),
        },
    }