"""
AuraQuant - Database Models for Paper Trading
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaperAccount(Base):
    """
    Represents a simulated trading account for a user.
    """
    __tablename__ = "paper_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), default="Default Paper Account")
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    starting_balance: Mapped[float] = mapped_column(Float, default=100000.0)
    current_balance: Mapped[float] = mapped_column(Float, default=100000.0)
    equity: Mapped[float] = mapped_column(Float, default=100000.0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="paper_account")
    positions: Mapped[List["PaperPosition"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    trades: Mapped[List["PaperTrade"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class PaperPosition(Base):
    """
    Represents an open position in a paper trading account.
    """
    __tablename__ = "paper_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("paper_accounts.id"))

    symbol: Mapped[str] = mapped_column(String(50), index=True)
    side: Mapped[str] = mapped_column(String(10))  # 'BUY' or 'SELL'
    volume: Mapped[float] = mapped_column(Float)
    open_price: Mapped[float] = mapped_column(Float)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    account: Mapped["PaperAccount"] = relationship(back_populates="positions")


class PaperTrade(Base):
    """
    Represents a closed trade (a deal) in a paper trading account.
    """
    __tablename__ = "paper_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("paper_accounts.id"))

    symbol: Mapped[str] = mapped_column(String(50), index=True)
    side: Mapped[str] = mapped_column(String(10))
    volume: Mapped[float] = mapped_column(Float)
    open_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    profit: Mapped[float] = mapped_column(Float)

    account: Mapped["PaperAccount"] = relationship(back_populates="trades")