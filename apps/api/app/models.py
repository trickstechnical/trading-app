from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    UniqueConstraint,
    Numeric,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Instrument(db.Model):
    __tablename__ = "instruments"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    exchange = db.Column(db.String(16), nullable=False)
    instrument_type = db.Column(db.String(20), nullable=False)
    tradable = db.Column(db.Boolean, nullable=False, default=True)
    candles = db.relationship("Candle", back_populates="instrument",
                              cascade="all, delete-orphan")

class Candle(db.Model):
    __tablename__ = "candles"
    id = db.Column(db.BigInteger, primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey("instruments.id", ondelete="CASCADE"),
                              nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    interval = db.Column(db.String(8), nullable=False, default="5m")
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    instrument = db.relationship("Instrument", back_populates="candles")
    __table_args__ = (
        db.UniqueConstraint("instrument_id", "timestamp", "interval",
                            name="uq_candle_instrument_time_interval"),
        db.Index("ix_candles_instrument_interval_timestamp",
                 "instrument_id", "interval", "timestamp"),
    )

class Signal(db.Model):
    __tablename__ = "signals"

    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(
        db.Integer, db.ForeignKey("instruments.id"), nullable=False
    )
    candle_timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL, WAIT
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)


class PaperAccount(db.Model):
    __tablename__ = "paper_accounts"

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)

    initial_balance = db.Column(
        Numeric(14, 2), nullable=False, default=100000
    )
    balance = db.Column(Numeric(14, 2), nullable=False, default=100000)

    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    positions = relationship("PaperPosition", back_populates="account")
    orders = relationship("PaperOrder", back_populates="account")


class PaperPosition(db.Model):
    __tablename__ = "paper_positions"

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "instrument_id",
            name="uq_paper_position_account_instrument",
        ),
        CheckConstraint("quantity >= 0", name="ck_paper_position_quantity"),
    )

    id = db.Column(Integer, primary_key=True)

    account_id = db.Column(
        Integer,
        ForeignKey("paper_accounts.id"),
        nullable=False,
    )

    instrument_id = db.Column(
        Integer,
        ForeignKey("instruments.id"),
        nullable=False,
    )

    entry_charges = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    total_entry_value = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    quantity = db.Column(Integer, nullable=False, default=0)

    average_price = db.Column(Numeric(14, 2), nullable=False)

    stop_loss = db.Column(Numeric(14, 2), nullable=True)
    target_price = db.Column(Numeric(14, 2), nullable=True)

    updated_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    account = relationship("PaperAccount", back_populates="positions")
    instrument = relationship("Instrument")


class PaperOrder(db.Model):
    __tablename__ = "paper_orders"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_paper_order_quantity"),
        CheckConstraint(
            "side IN ('BUY', 'SELL')",
            name="ck_paper_order_side",
        ),
    )

    id = db.Column(Integer, primary_key=True)

    account_id = db.Column(
        Integer,
        ForeignKey("paper_accounts.id"),
        nullable=False,
    )

    instrument_id = db.Column(
        Integer,
        ForeignKey("instruments.id"),
        nullable=False,
    )

    side = db.Column(String(4), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    price = db.Column(Numeric(14, 2), nullable=False)
    total_value = db.Column(Numeric(14, 2), nullable=False)

    status = db.Column(String(20), nullable=False, default="FILLED")
    order_type = db.Column(String(20), nullable=False, default="MARKET")

    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    charges = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    account = relationship("PaperAccount", back_populates="orders")
    instrument = relationship("Instrument")


class PaperTrade(db.Model):
    """A completed or partially completed SELL execution."""

    __tablename__ = "paper_trades"

    id = db.Column(Integer, primary_key=True)

    account_id = db.Column(
        Integer,
        ForeignKey("paper_accounts.id"),
        nullable=False,
    )

    instrument_id = db.Column(
        Integer,
        ForeignKey("instruments.id"),
        nullable=False,
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("paper_orders.id"),
        nullable=False,
        unique=True,
    )

    entry_charges = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    exit_charges = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    gross_pnl = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    net_pnl = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0,
    )

    quantity = db.Column(Integer, nullable=False)
    entry_price = db.Column(Numeric(14, 2), nullable=False)
    exit_price = db.Column(Numeric(14, 2), nullable=False)

    realized_pnl = db.Column(Numeric(14, 2), nullable=False)

    exit_reason = db.Column(
        String(30),
        nullable=False,
        default="MANUAL",
    )

    created_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    instrument = db.relationship("Instrument")