from decimal import Decimal

from app.paper_trading.charges import (
    calculate_equity_delivery_charges,
)


def test_buy_charges():
    result = calculate_equity_delivery_charges(
        price=Decimal("1000"),
        quantity=10,
        side="BUY",
    )

    assert result["turnover"] == Decimal("10000.00")
    assert result["brokerage"] == Decimal("20.00")
    assert result["stt"] == Decimal("10.00")
    assert result["stamp_duty"] == Decimal("1.50")
    assert result["dp_charges"] == Decimal("0.00")
    assert result["total_charges"] > Decimal("0")


def test_sell_charges():
    result = calculate_equity_delivery_charges(
        price=Decimal("1000"),
        quantity=10,
        side="SELL",
    )

    assert result["turnover"] == Decimal("10000.00")
    assert result["brokerage"] == Decimal("20.00")
    assert result["stt"] == Decimal("10.00")
    assert result["stamp_duty"] == Decimal("0.00")
    assert result["dp_charges"] == Decimal("12.50")
    assert result["total_charges"] > Decimal("0")


def test_small_order_brokerage():
    result = calculate_equity_delivery_charges(
        price=Decimal("100"),
        quantity=1,
        side="BUY",
    )

    assert result["brokerage"] == Decimal("0.30")


def test_invalid_side():
    try:
        calculate_equity_delivery_charges(
            price=Decimal("100"),
            quantity=1,
            side="INVALID",
        )
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_sell_pnl_accounting():
    exit_price = Decimal("1050")
    quantity = 10
    average_price = Decimal("1000")
    position_entry_charges = Decimal("20.00")
    position_quantity = 10

    sell_charges = calculate_equity_delivery_charges(
        price=exit_price,
        quantity=quantity,
        side="SELL",
    )["total_charges"]

    sell_value = exit_price * quantity
    allocated_entry_charges = (
        position_entry_charges * Decimal(quantity) / Decimal(position_quantity)
    )
    gross_pnl = sell_value - average_price * quantity
    net_pnl = gross_pnl - allocated_entry_charges - sell_charges

    assert sell_value == Decimal("10500")
    assert gross_pnl == Decimal("500")
    assert allocated_entry_charges == Decimal("20.00")
    assert net_pnl < gross_pnl
    assert net_pnl == gross_pnl - allocated_entry_charges - sell_charges


def test_sell_pnl_accounting():
    exit_price = Decimal("1050")
    quantity = 10
    average_price = Decimal("1000")
    position_entry_charges = Decimal("20.00")
    position_quantity = 10

    sell_charges = calculate_equity_delivery_charges(
        price=exit_price,
        quantity=quantity,
        side="SELL",
    )["total_charges"]

    sell_value = exit_price * quantity
    allocated_entry_charges = (
        position_entry_charges * Decimal(quantity) / Decimal(position_quantity)
    )
    gross_pnl = sell_value - average_price * quantity
    net_pnl = gross_pnl - allocated_entry_charges - sell_charges

    assert sell_value == Decimal("10500")
    assert gross_pnl == Decimal("500")
    assert allocated_entry_charges == Decimal("20.00")
    assert net_pnl < gross_pnl
    assert net_pnl == gross_pnl - allocated_entry_charges - sell_charges
