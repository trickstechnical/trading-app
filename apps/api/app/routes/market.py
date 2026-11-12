from datetime import date, datetime, time, timezone
from flask import Blueprint, jsonify, request
from app.models import Candle, Instrument

market_bp = Blueprint("market", __name__, url_prefix="/api/market")

@market_bp.get("/instruments")
def list_instruments():
    rows = Instrument.query.order_by(Instrument.symbol).all()
    return jsonify([{"id": x.id, "symbol": x.symbol, "name": x.name,
        "exchange": x.exchange, "instrument_type": x.instrument_type,
        "tradable": x.tradable} for x in rows])

@market_bp.get("/candles")
def get_candles():
    symbol, start, end = (request.args.get(k) for k in ("symbol", "start", "end"))
    interval = request.args.get("interval", "5m")
    if not all((symbol, start, end)):
        return jsonify(error="symbol, start, and end are required"), 400
    if interval != "5m":
        return jsonify(error="Only interval=5m is supported"), 400
    try:
        start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
        if end_date < start_date:
            raise ValueError()
    except ValueError:
        return jsonify(error="Dates must be YYYY-MM-DD and start <= end"), 400
    instrument = Instrument.query.filter_by(symbol=symbol).first()
    if instrument is None:
        return jsonify(error="Instrument not found"), 404
    start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
    rows = Candle.query.filter(Candle.instrument_id == instrument.id,
        Candle.interval == interval, Candle.timestamp >= start_dt,
        Candle.timestamp <= end_dt).order_by(Candle.timestamp.asc()).all()
    return jsonify({"symbol": symbol, "interval": interval, "count": len(rows),
        "candles": [{"timestamp": x.timestamp.isoformat(), "open": x.open,
            "high": x.high, "low": x.low, "close": x.close, "volume": x.volume}
            for x in rows]})