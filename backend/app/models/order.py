"""
AuraQuant - Orchestrated Order Database Model
"""
import enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Float, Boolean, JSON, Enum as SQLAlchemyEnum, ForeignKey, func, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, enum.Enum):
    """
    Defines the lifecycle states of an order within our orchestration engine.
    """
    # Initial state
    PENDING_SUBMIT = "pending_submit"  # Order created in our DB, not yet sent to exchange.

    # Active states
    SUBMITTED = "submitted"  # Order sent to exchange, awaiting confirmation of acceptance.
    ACCEPTED = "accepted"  # Exchange has accepted the order (it's now "working" or "open").
    PARTIALLY_FILLED = "partially_filled"  # A portion of the order has been executed.

    # Terminal states (end of life)
    FILLED = "filled"  # The order has been fully executed.
    CANCELED = "canceled"  # The order was successfully canceled.
    REJECTED = "rejected"  # The exchange rejected the order submission.
    EXPIRED = "expired"  # The order expired (e.g., Time-in-force).
    ERROR = "error"  # An unknown error occurred.


class OrchestratedOrder(Base):
    """
    Represents the state of a single trade order as managed by our internal
    orchestration engine. This table is the single source of truth.
    """
    __tablename__ = "orchestrated_orders"

    # Internal Identifiers
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Exchange & Symbol Information
    exchange: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Exchange-side Identifiers (populated after submission)
    exchange_order_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    # Core Order Parameters
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., 'LIMIT', 'MARKET'
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., 'BUY', 'SELL'
    quantity_requested: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float)  # Entry price for LIMIT/STOP orders

    # State Management
    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING_SUBMIT, index=True
    )
    quantity_filled: Mapped[float] = mapped_column(Float, default=0.0)
    average_fill_price: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamps & Auditing
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    filled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Error & Metadata
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    order_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # For SL/TP, strategy_id, etc.

    parent_order_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("orchestrated_orders.id"), index=True)
    is_algorithmic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    child_orders: Mapped[List["OrchestratedOrder"]] = relationship("OrchestratedOrder")

    is_paper_trade: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    user: Mapped["User"] = relationship()

    def __repr__(self):
        return (
            f"<OrchestratedOrder(id={self.id}, exchange='{self.exchange}', symbol='{self.symbol}', "
            f"status='{self.status}', quantity={self.quantity_requested})>"
        )