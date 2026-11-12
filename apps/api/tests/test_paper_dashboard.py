from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models import Candle, PaperPosition
from app.paper_trading.dashboard import get_dashboard


def test_dashboard_unrealized_pnl_uses_latest_completed_candle(
    app, db, paper_account, instrument
):
    now = datetime.now(timezone.utc)

    completed_candle = Candle(
        id=1,
        instrument_id=instrument.id,
        timestamp=now - timedelta(minutes=10),
        interval="5m",
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=1000,
    )

    incomplete_candle = Candle(
        id=2,
        instrument_id=instrument.id,
        timestamp=now - timedelta(minutes=2),
        interval="5m",
        open=105.0,
        high=120.0,
        low=104.0,
        close=118.0,
        volume=500,
    )

    position = PaperPosition(
        account_id=paper_account.id,
        instrument_id=instrument.id,
        quantity=10,
        average_price=Decimal("100.00"),
        entry_charges=Decimal("5.00"),
        total_entry_value=Decimal("1000.00"),
    )

    db.session.add_all([completed_candle, incomplete_candle, position])
    db.session.commit()

    dashboard = get_dashboard(account_id=paper_account.id)
    pos_data = dashboard["positions"][0]

    # Current price must be from the completed candle (105.0), NOT the incomplete candle (118.0)
    assert pos_data["current_price"] == 105.0

    # Unrealized P&L = (105.0 - 100.00) * 10 = 50.0
    expected_unrealized_pnl = (
        Decimal(str(pos_data["current_price"]))
        - Decimal(str(position.average_price))
    ) * Decimal(str(position.quantity))

    assert pos_data["unrealized_pnl"] == float(expected_unrealized_pnl)
    assert dashboard["account"]["unrealized_pnl"] == float(expected_unrealized_pnl)
    assert pos_data["market_value"] == 1050.0
