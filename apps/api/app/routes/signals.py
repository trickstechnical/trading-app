from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Candle, Instrument
from app.strategy.signal_engine import generate_signal

signals_bp = Blueprint("signals", __name__, url_prefix="/api/signals")

CANDLE_INTERVAL = "5m"
CANDLE_DURATION = timedelta(minutes=5)
MAX_CANDLES = 500

# Keep this list aligned with the symbols in your Phase 2 symbols.py.
ALLOWED_SYMBOLS = {
    "NSE:SBIN-EQ",
    "NSE:NIFTY50-INDEX",
}


@signals_bp.get("/latest")
def get_latest_signal():
    symbol = request.args.get("symbol", "NSE:SBIN-EQ").strip()

    if symbol not in ALLOWED_SYMBOLS:
        return jsonify({
            "error": "Unsupported symbol",
            "allowed_symbols": sorted(ALLOWED_SYMBOLS),
        }), 400

    candles = (
        db.session.query(Candle)
        .join(Instrument, Candle.instrument_id == Instrument.id)
        .filter(
            Instrument.symbol == symbol,
            Candle.interval == CANDLE_INTERVAL,
        )
        .order_by(Candle.timestamp.desc())
        .limit(MAX_CANDLES)
        .all()
    )

    if not candles:
        return jsonify({
            "error": "No candle data found for this symbol",
            "symbol": symbol,
        }), 404

    # The database query returns newest first; the strategy needs oldest first.
    candles.reverse()

    now = datetime.now(timezone.utc)

    completed_candles = []

    for candle in candles:
        timestamp = candle.timestamp

        # Treat naive database timestamps as UTC.
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)

        # Do not use a candle until its full five-minute interval has ended.
        if timestamp + CANDLE_DURATION > now:
            continue

        completed_candles.append({
            "timestamp": timestamp,
            "open": float(candle.open),
            "high": float(candle.high),
            "low": float(candle.low),
            "close": float(candle.close),
            "volume": float(candle.volume),
        })

    if len(completed_candles) < 60:
        return jsonify({
            "error": "Not enough completed candles to generate a signal",
            "symbol": symbol,
            "required_candles": 60,
            "available_candles": len(completed_candles),
        }), 422

    try:
        result = generate_signal(completed_candles)

        return jsonify({
            "symbol": symbol,
            "interval": CANDLE_INTERVAL,
            **result,
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error),
            "symbol": symbol,
        }), 422