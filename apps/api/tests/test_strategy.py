from datetime import datetime, timedelta, timezone

import pytest

from app.strategy.indicators import (
    calculate_atr,
    calculate_average_volume,
    calculate_ema,
    calculate_session_vwap,
)
from app.strategy.rules import calculate_scores
from app.strategy.signal_engine import generate_signal


def make_candles(count=70, direction="up"):
    candles = []

    for index in range(count):
        if direction == "up":
            open_price = 100 + index
            close_price = open_price + 1
        elif direction == "down":
            open_price = 200 - index
            close_price = open_price - 1
        else:
            open_price = 100
            close_price = 100

        candles.append({
            "timestamp": (
                datetime(2026, 10, 1, 9, 15, tzinfo=timezone.utc)
                + timedelta(minutes=5 * index)
            ),
            "open": float(open_price),
            "high": float(max(open_price, close_price) + 0.5),
            "low": float(min(open_price, close_price) - 0.5),
            "close": float(close_price),
            "volume": 1000.0,
        })

    return candles


def test_calculate_ema():
    result = calculate_ema([10, 11, 12, 13, 14], 3)

    assert result > 12


def test_calculate_atr():
    candles = make_candles(20)

    result = calculate_atr(candles, 14)

    assert result > 0


def test_calculate_average_volume():
    candles = make_candles(25)

    result = calculate_average_volume(candles, 20)

    assert result == 1000


def test_calculate_session_vwap():
    candles = make_candles(20)

    result = calculate_session_vwap(candles)

    assert result > 0


def test_buy_signal():
    candles = make_candles(70, "up")

    result = generate_signal(candles)

    assert result["signal"] in {"BUY", "HOLD"}
    assert result["buy_score"] >= 0
    assert result["sell_score"] >= 0


def test_sell_signal():
    candles = make_candles(70, "down")

    result = generate_signal(candles)

    assert result["signal"] in {"SELL", "HOLD"}
    assert result["buy_score"] >= 0
    assert result["sell_score"] >= 0


def test_hold_signal_when_scores_are_low():
    candles = make_candles(70, "flat")

    result = generate_signal(candles)

    assert result["signal"] == "HOLD"


def test_insufficient_candles():
    candles = make_candles(20)

    with pytest.raises(ValueError):
        generate_signal(candles)


def test_buy_scoring_threshold():
    candles = make_candles(2, "up")

    result = calculate_scores(
        candles=candles,
        ema20=110,
        ema50=100,
        vwap=90,
        average_volume=1000,
    )

    assert result["signal"] == "BUY"
    assert result["buy_score"] == 80


def test_sell_scoring_threshold():
    candles = make_candles(2, "down")

    result = calculate_scores(
        candles=candles,
        ema20=90,
        ema50=100,
        vwap=300,
        average_volume=1000,
    )

    assert result["signal"] == "SELL"
    assert result["sell_score"] == 80