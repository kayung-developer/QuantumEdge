"""
AuraQuant - Database Models for Adaptive Strategy Deployment
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AdaptivePortfolio(Base):
    """
    Represents a user's configuration for a regime-aware adaptive portfolio.
    """
    __tablename__ = "adaptive_portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=False)

    # This JSON blob stores the core logic: { "regime_0": "strategy_id_1", "regime_1": "strategy_id_2", ... }
    regime_strategy_map: Mapped[Dict[str, Any]] = mapped_column(JSON)

    user: Mapped["User"] = relationship()