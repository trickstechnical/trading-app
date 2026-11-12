import os
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from app.market_data.base import MarketDataAdapter

class FyersAdapter(MarketDataAdapter):
    # Historical-data adapter only. No order-placement methods are used.
    def __init__(self, client_id: str | None = None, access_token: str | None = None):
        self.client_id = client_id or os.getenv("FYERS_CLIENT_ID")
        token = access_token or os.getenv("FYERS_ACCESS_TOKEN")
        if not self.client_id or not token:
            raise RuntimeError("Set FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN.")
        try:
            from fyers_apiv3 import fyersModel
        except ImportError as exc:
            raise RuntimeError("Install FYERS SDK: pip install fyers-apiv3") from exc
        self.client = fyersModel.FyersModel(
            client_id=self.client_id, token=token, is_async=False, log_path=""
        )

    def fetch_candles(self, symbol: str, start_date: date, end_date: date,
                      resolution: str = "5") -> list[dict[str, Any]]:
        if end_date < start_date:
            raise ValueError("end_date must be on or after start_date")
        result = []
        chunk_start = start_date
        while chunk_start <= end_date:
            chunk_end = min(chunk_start + timedelta(days=90), end_date)
            start_dt = datetime.combine(chunk_start, time.min, tzinfo=timezone.utc)
            end_dt = datetime.combine(chunk_end + timedelta(days=1), time.min,
                                      tzinfo=timezone.utc) - timedelta(seconds=1)
            payload = {
                "symbol": symbol, "resolution": resolution, "date_format": "0",
                "range_from": str(int(start_dt.timestamp())),
                "range_to": str(int(end_dt.timestamp())), "cont_flag": "1",
            }
            response = self.client.history(data=payload)
            if not isinstance(response, dict) or response.get("s") != "ok":
                message = response.get("message", "Unknown FYERS error") if isinstance(response, dict) else str(response)
                raise RuntimeError(f"FYERS history failed for {symbol}: {message}")
            for row in response.get("candles", []):
                if isinstance(row, (list, tuple)) and len(row) >= 6:
                    result.append(dict(timestamp=row[0], open=row[1], high=row[2],
                                       low=row[3], close=row[4], volume=row[5]))
            chunk_start = chunk_end + timedelta(days=1)
        return result