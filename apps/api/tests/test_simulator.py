import pytest

from app.paper.simulator import PaperAccount, PaperSimulator


def test_account_starts_with_100000():
    simulator = PaperSimulator()
    assert simulator.account.cash == 100_000


def test_buy_and_sell_records_pnl():
    account = PaperAccount(cash=100_000)
    simulator = PaperSimulator(account, slippage_bps=0, fee_rate=0)

    buy = simulator.buy(market_price=100, quantity=10)

    assert buy["status"] == "FILLED"
    assert account.cash == 99_000
    assert account.position.quantity == 10

    sell = simulator.sell(market_price=110)

    assert sell["status"] == "FILLED"
    assert sell["realised_pnl"] == 100
    assert account.cash == 100_100
    assert account.position is None


def test_rejects_buy_without_enough_cash():
    simulator = PaperSimulator(PaperAccount(cash=100))

    with pytest.raises(ValueError):
        simulator.buy(market_price=100, quantity=2)


def test_rejects_sell_without_open_position():
    simulator = PaperSimulator()

    with pytest.raises(ValueError, match="No open position"):
        simulator.sell(market_price=100)


def test_rejects_second_open_position():
    simulator = PaperSimulator()
    simulator.buy(market_price=100, quantity=1)

    with pytest.raises(ValueError, match="Only one open position"):
        simulator.buy(market_price=105, quantity=1)