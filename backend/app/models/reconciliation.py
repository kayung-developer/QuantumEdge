"""
AuraQuant - Database Model for Reconciliation Reports
"""
import enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime,
                        func, Text, Float, Boolean, Integer)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReconciliationStatus(str, enum.Enum):
    SUCCESS = "success"  # All records matched perfectly.
    WARNING = "warning"  # Some non-critical discrepancies were found.
    FAILURE = "failure"  # Critical discrepancies found that require manual intervention.
    RUNNING = "running"


class ReconciliationReport(Base):
    """
    Stores the results of a single reconciliation run for a specific exchange.
    """
    __tablename__ = "reconciliation_reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    exchange_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    status: Mapped[ReconciliationStatus] = mapped_column(SQLAlchemyEnum(ReconciliationStatus), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    duration_seconds: Mapped[float] = mapped_column(Float)

    # --- Summary Metrics ---
    internal_trades_checked: Mapped[int] = mapped_column(Integer)
    external_trades_fetched: Mapped[int] = mapped_column(Integer)
    matched_trades: Mapped[int] = mapped_column(Integer)
    mismatched_trades: Mapped[int] = mapped_column(Integer)
    missing_internal: Mapped[int] = mapped_column(Integer)  # Trades found externally but not in our DB
    missing_external: Mapped[int] = mapped_column(Integer)  # Trades in our DB but not found externally

    # --- Detailed Discrepancies ---
    # We store the actual mismatched records as JSON for detailed analysis.
    discrepancies: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)