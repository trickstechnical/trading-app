import pytest

from app import create_app
from app.config import Config
from app.extensions import db as _db
from app.models import Instrument, PaperAccount


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    START_PAPER_SCHEDULER = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def paper_account(db):
    account = PaperAccount(
        id=1,
        name="Test Paper Account",
        initial_balance=100000,
        balance=100000,
    )
    db.session.add(account)
    db.session.commit()
    return account


@pytest.fixture
def instrument(db):
    instrument = Instrument(
        symbol="NSE:SBIN-EQ",
        name="State Bank of India",
        exchange="NSE",
        instrument_type="EQUITY",
        tradable=True,
    )
    db.session.add(instrument)
    db.session.commit()
    return instrument

