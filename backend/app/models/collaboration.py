"""
AuraQuant - Database Models for Collaboration and Social Trading
"""
import enum
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (ForeignKey, String, Enum as SQLAlchemyEnum, JSON, DateTime,
                        func, Text, Float, Boolean, Integer, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TradeRoomRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TradeRoom(Base):
    """
    Represents a collaborative space where users can chat and share trades.
    """
    __tablename__ = "trade_rooms"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship()
    members: Mapped[List["TradeRoomMember"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    messages: Mapped[List["ChatMessage"]] = relationship(back_populates="room", cascade="all, delete-orphan")


class TradeRoomMember(Base):
    """
    Association table for users and their roles within a Trade Room.
    """
    __tablename__ = "trade_room_members"
    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='_room_user_uc'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("trade_rooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    role: Mapped[TradeRoomRole] = mapped_column(SQLAlchemyEnum(TradeRoomRole), default=TradeRoomRole.MEMBER)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    room: Mapped["TradeRoom"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ChatMessage(Base):
    """
    Represents a single message sent within a Trade Room.
    """
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("trade_rooms.id"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    room: Mapped["TradeRoom"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()


class CopyTradeSubscription(Base):
    """
    Represents a user's subscription to copy trades from another user (the leader).
    """
    __tablename__ = "copy_trade_subscriptions"
    __table_args__ = (UniqueConstraint('follower_id', 'leader_id', name='_follower_leader_uc'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Risk Management for the Follower ---
    max_trade_size_usd: Mapped[float] = mapped_column(Float)
    trade_size_multiplier: Mapped[float] = mapped_column(Float, default=1.0, comment="e.g., 0.5 to copy at half size.")

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    follower: Mapped["User"] = relationship(foreign_keys=[follower_id])
    leader: Mapped["User"] = relationship(foreign_keys=[leader_id])