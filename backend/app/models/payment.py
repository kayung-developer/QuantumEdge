"""
AuraQuant - Payment Transaction Database Model
"""
import enum
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, String, Float, DateTime, Enum as SQLAlchemyEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    """
    Enum for the status of a payment transaction.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """
    Represents a single payment transaction.
    """
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    subscription_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subscriptions.id"))

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLAlchemyEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )

    # Payment Provider Information
    provider: Mapped[str] = mapped_column(String(50), nullable=False, comment="e.g., 'paystack', 'paypal'")
    provider_transaction_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True,
                                                         comment="The unique transaction ID from the payment provider.")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    user: Mapped["User"] = relationship()  # Implicit back-populates
    subscription: Mapped[Optional["Subscription"]] = relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"