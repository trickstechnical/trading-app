from decimal import Decimal

from app.models import Instrument, PaperOrder, PaperTrade
from app.paper_trading.analytics import calculate_metrics


def test_empty_account_returns_zero_metrics(app, db):
    result = calculate_metrics(account_id=1)

    assert result["total_trades"] == 0
    assert result["win_rate"] == 0.0
    assert result["net_pnl"] == 0.0
    assert result["profit_factor"] is None


def test_analytics_with_completed_trades(app, db, paper_account):
    instrument = Instrument.query.filter_by(symbol="NSE:SBIN-EQ").first()
    if not instrument:
        instrument = Instrument(
            symbol="NSE:SBIN-EQ",
            name="State Bank of India",
            exchange="NSE",
            instrument_type="EQUITY",
            tradable=True,
        )
        db.session.add(instrument)
        db.session.commit()

    trades_data = [
        {"pnl": Decimal("500.00"), "qty": 10, "entry": Decimal("100.00"), "exit": Decimal("150.00")},
        {"pnl": Decimal("300.00"), "qty": 10, "entry": Decimal("100.00"), "exit": Decimal("130.00")},
        {"pnl": Decimal("-200.00"), "qty": 10, "entry": Decimal("100.00"), "exit": Decimal("80.00")},
    ]

    for index, data in enumerate(trades_data, start=1):
        order = PaperOrder(
            id=index,
            account_id=paper_account.id,
            instrument_id=instrument.id,
            side="SELL",
            quantity=data["qty"],
            price=data["exit"],
            total_value=data["exit"] * data["qty"],
            status="FILLED",
            order_type="MARKET",
        )
        db.session.add(order)
        db.session.flush()

        trade = PaperTrade(
            account_id=paper_account.id,
            instrument_id=instrument.id,
            order_id=order.id,
            quantity=data["qty"],
            entry_price=data["entry"],
            exit_price=data["exit"],
            gross_pnl=data["pnl"],
            net_pnl=data["pnl"],
            realized_pnl=data["pnl"],
            exit_reason="MANUAL",
        )
        db.session.add(trade)

    db.session.commit()

    result = calculate_metrics(account_id=paper_account.id)

    assert result["total_trades"] == 3
    assert result["winning_trades"] == 2
    assert result["losing_trades"] == 1
    assert result["win_rate"] == 66.67
    assert result["net_pnl"] == 600.0


def test_analytics_with_only_winning_trades_returns_none_profit_factor(app, db, paper_account):
    instrument = Instrument.query.filter_by(symbol="NSE:TCS-EQ").first()
    if not instrument:
        instrument = Instrument(
            symbol="NSE:TCS-EQ",
            name="Tata Consultancy Services",
            exchange="NSE",
            instrument_type="EQUITY",
            tradable=True,
        )
        db.session.add(instrument)
        db.session.commit()

    order = PaperOrder(
        id=101,
        account_id=paper_account.id,
        instrument_id=instrument.id,
        side="SELL",
        quantity=5,
        price=Decimal("3500.00"),
        total_value=Decimal("17500.00"),
        status="FILLED",
        order_type="MARKET",
    )
    db.session.add(order)
    db.session.flush()

    trade = PaperTrade(
        account_id=paper_account.id,
        instrument_id=instrument.id,
        order_id=order.id,
        quantity=5,
        entry_price=Decimal("3400.00"),
        exit_price=Decimal("3500.00"),
        gross_pnl=Decimal("500.00"),
        net_pnl=Decimal("500.00"),
        realized_pnl=Decimal("500.00"),
        exit_reason="TARGET",
    )
    db.session.add(trade)
    db.session.commit()

    result = calculate_metrics(account_id=paper_account.id)

    assert result["total_trades"] == 1
    assert result["winning_trades"] == 1
    assert result["losing_trades"] == 0
    assert result["profit_factor"] is None

