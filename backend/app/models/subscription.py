"""
AuraQuant - User Subscription Database Model
"""
import enum
from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubscriptionStatus(str, enum.Enum):
    """
    Enum for the status of a user's subscription.
    """
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"


class Subscription(Base):
    """
    Represents a user's subscription to a specific plan.
    """
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)

    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLAlchemyEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.INCOMPLETE
    )

    # Timestamps
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Payment Provider Information
    provider: Mapped[Optional[str]] = mapped_column(String(50), comment="e.g., 'paystack', 'paypal'")
    provider_subscription_id: Mapped[Optional[str]] = mapped_column(String(255),
                                                                    comment="The subscription ID from the payment provider for recurring billing.")

    # --- Relationships ---
    user: Mapped["User"] = relationship()  # Implicit back-populates from User
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")
    payments: Mapped[List["Payment"]] = relationship(back_populates="subscription")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id}, status='{self.status}')>"