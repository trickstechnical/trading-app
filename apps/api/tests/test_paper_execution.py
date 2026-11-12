from decimal import Decimal

from app.paper_trading.execution import get_exit_price


STOP = Decimal("800")
TARGET = Decimal("840")


def test_stop_loss_gap():
    result = get_exit_price(
        Decimal("795"),
        Decimal("810"),
        Decimal("790"),
        STOP,
        TARGET,
    )

    assert result == (Decimal("795"), "STOP_LOSS")


def test_stop_loss_hit():
    result = get_exit_price(
        Decimal("810"),
        Decimal("820"),
        Decimal("795"),
        STOP,
        TARGET,
    )

    assert result == (STOP, "STOP_LOSS")


def test_target_hit():
    result = get_exit_price(
        Decimal("810"),
        Decimal("845"),
        Decimal("805"),
        STOP,
        TARGET,
    )

    assert result == (TARGET, "TARGET")


def test_target_gap():
    result = get_exit_price(
        Decimal("850"),
        Decimal("860"),
        Decimal("845"),
        STOP,
        TARGET,
    )

    assert result == (TARGET, "TARGET")


def test_both_levels_hit_stop_loss_first():
    result = get_exit_price(
        Decimal("810"),
        Decimal("845"),
        Decimal("795"),
        STOP,
        TARGET,
    )

    assert result == (STOP, "STOP_LOSS")


def test_no_exit():
    result = get_exit_price(
        Decimal("810"),
        Decimal("830"),
        Decimal("805"),
        STOP,
        TARGET,
    )

    assert result is None