"""
AuraQuant - Database Models for the Strategy Marketplace
"""
import enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime,
                        func, Text, Float, Boolean, Integer)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MarketplaceStrategyStatus(str, enum.Enum):
    PRIVATE = "private"  # User is developing it, not visible to others.
    PENDING = "pending"  # Submitted for review by platform admins.
    APPROVED = "approved"  # Live on the marketplace and available for subscription.
    REJECTED = "rejected"  # Rejected by admin review.
    ARCHIVED = "archived"  # Removed from the marketplace by the author.


class MarketplaceStrategy(Base):
    """
    Represents a user-created strategy that has been published to the marketplace.
    """
    __tablename__ = "marketplace_strategies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # The actual Python code for the strategy, encrypted for security.
    encrypted_code: Mapped[bytes] = mapped_column(nullable=False)

    # --- Marketplace Details ---
    status: Mapped[MarketplaceStrategyStatus] = mapped_column(SQLAlchemyEnum(MarketplaceStrategyStatus),
                                                              default=MarketplaceStrategyStatus.PRIVATE)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Pricing for subscribing to this strategy
    subscription_price_monthly: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # --- Verified Performance ---
    # The platform runs a mandatory, standardized backtest and stores the results here.
    # This prevents authors from showing misleading or cherry-picked results.
    verified_performance_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    author: Mapped["User"] = relationship(back_populates="published_strategies")
    subscriptions: Mapped[List["MarketplaceSubscription"]] = relationship(back_populates="strategy")


class MarketplaceSubscription(Base):
    """
    Represents a user's subscription to a specific marketplace strategy.
    """
    __tablename__ = "marketplace_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    strategy_id: Mapped[UUID] = mapped_column(ForeignKey("marketplace_strategies.id"), index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # This links to a payment in our main payment table
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"))

    subscriber: Mapped["User"] = relationship(foreign_keys=[subscriber_id])
    strategy: Mapped["MarketplaceStrategy"] = relationship(back_populates="subscriptions")