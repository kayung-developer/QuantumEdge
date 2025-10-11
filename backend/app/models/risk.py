"""
AuraQuant - Database Models for Risk Management
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Float, Integer, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
import datetime


class UserRiskProfile(Base):
    """
    Stores the specific risk management rules for a single user.
    If a user does not have a profile, default platform-wide rules apply.
    """
    __tablename__ = "user_risk_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # --- Position & Order Limits ---
    max_open_positions: Mapped[Optional[int]] = mapped_column(Integer,
                                                              comment="Maximum number of concurrent open positions.")
    max_order_value_usd: Mapped[Optional[float]] = mapped_column(Float, comment="Maximum USD value for a single order.")

    # --- Exposure Limits ---
    max_exposure_per_symbol_usd: Mapped[Optional[float]] = mapped_column(Float,
                                                                         comment="Maximum total USD exposure for any single symbol.")
    max_total_exposure_usd: Mapped[Optional[float]] = mapped_column(Float,
                                                                    comment="Maximum total USD exposure across all positions.")

    # --- Drawdown Limits ---
    max_daily_drawdown_pct: Mapped[Optional[float]] = mapped_column(Float,
                                                                    comment="Maximum allowed loss in a single day, as a percentage of account balance.")
    max_total_drawdown_pct: Mapped[Optional[float]] = mapped_column(Float,
                                                                    comment="Maximum allowed loss from the all-time high balance.")

    # --- Kill Switch ---
    # A global kill switch for a user. If true, no new trades are allowed.
    trading_halted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="risk_profile")

    def __repr__(self):
        return f"<UserRiskProfile(user_id={self.user_id}, trading_halted={self.trading_halted})>"
