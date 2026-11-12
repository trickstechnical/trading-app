import click
from datetime import date
from app.extensions import db
from app.market_data.fyers_adapter import FyersAdapter
from app.market_data.symbols import INSTRUMENTS
from app.market_data.validation import validate_candles
from app.models import Candle, Instrument

def get_or_create_instrument(config):
    instrument = Instrument.query.filter_by(symbol=config.symbol).first()
    if instrument is None:
        instrument = Instrument(symbol=config.symbol, name=config.name,
            exchange=config.exchange, instrument_type=config.instrument_type,
            tradable=config.tradable)
        db.session.add(instrument)
        db.session.flush()
    return instrument

def save_candles(instrument, candles, interval="5m"):
    processed = 0
    for item in candles:
        row = Candle.query.filter_by(instrument_id=instrument.id,
            timestamp=item["timestamp"], interval=interval).first()
        fields = {key: item[key] for key in ("open", "high", "low", "close", "volume")}
        if row is None:
            db.session.add(Candle(instrument_id=instrument.id,
                timestamp=item["timestamp"], interval=interval, **fields))
        else:
            for key, value in fields.items():
                setattr(row, key, value)
        processed += 1
    return processed

def ingest_historical_candles(start_date: date, end_date: date,
                              instrument_keys=None, adapter=None):
    adapter = adapter or FyersAdapter()
    results = {}
    for key in (instrument_keys or list(INSTRUMENTS)):
        config = INSTRUMENTS.get(key.upper())
        if config is None:
            raise ValueError(f"Unsupported instrument: {key}")
        raw = adapter.fetch_candles(config.symbol, start_date, end_date, "5")
        candles = validate_candles(raw)
        instrument = get_or_create_instrument(config)
        results[key.upper()] = save_candles(instrument, candles)
        db.session.commit()
    return results

def register_ingestion_command(app):
    @app.cli.command("ingest-candles")
    @click.option("--start", "start_value", required=True, help="YYYY-MM-DD")
    @click.option("--end", "end_value", required=True, help="YYYY-MM-DD")
    @click.option("--instruments", default="SBIN,NIFTY50", show_default=True)
    def ingest_candles(start_value, end_value, instruments):
        try:
            start_date, end_date = date.fromisoformat(start_value), date.fromisoformat(end_value)
            if end_date < start_date:
                raise ValueError("--end must be on or after --start")
            result = ingest_historical_candles(start_date, end_date,
                [part.strip().upper() for part in instruments.split(",") if part.strip()])
        except Exception as exc:
            db.session.rollback()
            raise click.ClickException(str(exc)) from exc
        for symbol, count in result.items():
            click.echo(f"{symbol}: processed {count} candles")
        click.echo("Ingestion completed.")