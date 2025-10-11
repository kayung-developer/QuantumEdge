"""
AuraQuant - Database Model for Audit Trails
"""
import enum
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditAction(str, enum.Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"

    ORDER_CREATE_REQUEST = "order_create_request"
    ORDER_STATE_CHANGE = "order_state_change"

    RISK_RULE_VIOLATION = "risk_rule_violation"
    RISK_PROFILE_UPDATE = "risk_profile_update"
    TRADING_HALTED = "trading_halted"
    TRADING_RESUMED = "trading_resumed"

    WITHDRAWAL_REQUEST = "withdrawal_request"
    DEPOSIT_CONFIRMED = "deposit_confirmed"


class AuditLog(Base):
    """
    Stores a log of all significant actions taken in the system for
    compliance and security auditing.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True,
                                                   comment="The user who performed the action.")

    action: Mapped[AuditAction] = mapped_column(SQLAlchemyEnum(AuditAction), nullable=False, index=True)

    details: Mapped[Optional[str]] = mapped_column(Text, comment="A human-readable description of the event.")

    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON,
                                                               comment="Structured data associated with the event (e.g., order details, IP address).")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"