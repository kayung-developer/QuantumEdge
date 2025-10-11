"""
AuraQuant - Subscription Plan Database Model
"""
from typing import List, Optional, Dict, Any

from sqlalchemy import String, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Plan(Base):
    """
    Represents a subscription plan available to users.
    """
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    # Pricing Information
    price_monthly: Mapped[float] = mapped_column(Float, nullable=False)
    price_yearly: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Features list, stored as JSON for flexibility
    # Example: {"max_bots": 5, "cv_analysis": true, "api_access": false}
    features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Control flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False,
                                            comment="Controls if the plan is visible on the public pricing page.")

    # --- Relationships ---
    # A plan can be associated with many user subscriptions.
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, name='{self.name}', price_monthly={self.price_monthly})>"