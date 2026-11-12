from dataclasses import dataclass

@dataclass(frozen=True)
class InstrumentConfig:
    symbol: str
    name: str
    exchange: str
    instrument_type: str
    tradable: bool

INSTRUMENTS = {
    "SBIN": InstrumentConfig("NSE:SBIN-EQ", "State Bank of India", "NSE", "EQUITY", True),
    "NIFTY50": InstrumentConfig("NSE:NIFTY50-INDEX", "NIFTY 50", "NSE", "INDEX", False),
}

def get_instrument(key: str) -> InstrumentConfig:
    try:
        return INSTRUMENTS[key.upper()]
    except KeyError as exc:
        raise ValueError(f"Unknown instrument '{key}'. Supported: {', '.join(INSTRUMENTS)}") from exc