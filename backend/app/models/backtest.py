"""
AuraQuant - Database Model for Backtest Results
"""
import enum
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BacktestStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BacktestSession(Base):
    """
    Stores the configuration and results of a single backtesting run.
    """
    __tablename__ = "backtest_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    strategy_name: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(50))
    timeframe: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    status: Mapped[BacktestStatus] = mapped_column(SQLAlchemyEnum(BacktestStatus), default=BacktestStatus.PENDING)

    # Results are stored as JSON for flexibility
    results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()