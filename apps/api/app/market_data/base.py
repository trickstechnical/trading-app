from abc import ABC, abstractmethod
from datetime import date
from typing import Any

class MarketDataAdapter(ABC):
    @abstractmethod
    def fetch_candles(self, symbol: str, start_date: date, end_date: date,
                      resolution: str = "5") -> list[dict[str, Any]]:
        raise NotImplementedError