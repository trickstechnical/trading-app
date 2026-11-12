def calculate_scores(
    candles: list[dict],
    ema20: float,
    ema50: float,
    vwap: float,
    average_volume: float,
) -> dict:
    current = candles[-1]
    previous = candles[-2]

    buy_score = 0
    sell_score = 0

    breakdown = {
        "trend": {"buy": 0, "sell": 0, "max": 30},
        "vwap": {"buy": 0, "sell": 0, "max": 25},
        "volume": {"buy": 0, "sell": 0, "max": 20},
        "price_action": {"buy": 0, "sell": 0, "max": 25},
    }

    # 1. Trend: 30 points
    if ema20 > ema50:
        buy_score += 30
        breakdown["trend"]["buy"] = 30
    elif ema20 < ema50:
        sell_score += 30
        breakdown["trend"]["sell"] = 30

    # 2. VWAP: 25 points
    if current["close"] > vwap:
        buy_score += 25
        breakdown["vwap"]["buy"] = 25
    elif current["close"] < vwap:
        sell_score += 25
        breakdown["vwap"]["sell"] = 25

    # 3. Volume confirmation: 20 points
    volume_confirmed = (
        average_volume > 0
        and current["volume"] >= average_volume * 1.2
    )

    if volume_confirmed:
        if current["close"] > current["open"]:
            buy_score += 20
            breakdown["volume"]["buy"] = 20
        elif current["close"] < current["open"]:
            sell_score += 20
            breakdown["volume"]["sell"] = 20

    # 4. Price action: 25 points
    if (
        current["close"] > current["open"]
        and current["close"] > previous["high"]
    ):
        buy_score += 25
        breakdown["price_action"]["buy"] = 25

    elif (
        current["close"] < current["open"]
        and current["close"] < previous["low"]
    ):
        sell_score += 25
        breakdown["price_action"]["sell"] = 25

    # Final signal
    signal = "HOLD"

    if buy_score >= 70 and buy_score - sell_score >= 20:
        signal = "BUY"

    elif sell_score >= 70 and sell_score - buy_score >= 20:
        signal = "SELL"

    return {
        "signal": signal,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "volume_confirmed": volume_confirmed,
        "breakdown": breakdown,
    }