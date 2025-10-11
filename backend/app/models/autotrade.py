"""
AuraQuant - Database Models for AutoML Strategy Forging
"""
import enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime,
                        func, Text, Float, Boolean)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ForgeJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ForgeJob(Base):
    """
    Represents a single AutoML Strategy Forging job initiated by a user.
    """
    __tablename__ = "forge_jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    status: Mapped[ForgeJobStatus] = mapped_column(SQLAlchemyEnum(ForgeJobStatus), default=ForgeJobStatus.PENDING)

    # --- Job Configuration ---
    strategy_id: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(50))
    timeframe: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    optimization_metric: Mapped[str] = mapped_column(String(50))  # e.g., "sharpe_ratio"

    # --- Job Results ---
    best_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    best_performance: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    top_permutations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()