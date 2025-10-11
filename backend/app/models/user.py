"""
AuraQuant - User Database Model

This module defines the `User` model, which represents the `users` table in the
database. This model is central to the application, storing all information related
to a user's account, permissions, and preferences.

Key Attributes:
-   `id`: The unique primary key for the user.
-   `email`: The user's email address, used for login. It is unique and indexed
    for fast lookups.
-   `hashed_password`: The securely hashed password. Plain-text passwords are
    never stored.
-   `full_name`: The user's full name.
-   `is_active`: A boolean flag to control whether the user's account is enabled.
    Inactive users cannot log in.
-   `is_superuser`: A boolean flag that grants administrative privileges. Superusers
    can manage other users, subscriptions, etc.
-   `created_at`, `updated_at`: Timestamps for tracking record creation and
    modification, crucial for auditing.
-   `last_login_at`: Tracks the last successful login time, useful for security
    audits and user activity monitoring.
-   `timezone`: Stores the user's preferred timezone (e.g., 'UTC', 'America/New_York')
    to ensure all time-based data is displayed correctly in their local context.
-   `language`: The user's preferred language for the UI (e.g., 'en', 'es').
-   `theme`: The user's preferred UI theme ('light', 'dark', 'system').
-   `firebase_device_token`: Stores the unique token for sending push notifications
    to the user's mobile device via Firebase Cloud Messaging.
-   `two_factor_secret`: An encrypted secret key for Time-based One-Time Password (TOTP)
    two-factor authentication. This should be handled with extreme care.
-   `is_two_factor_enabled`: A flag to indicate if 2FA is active for the account.
-   Relationships: Placeholders for future models like `Subscription`, `ApiKey`,
    `Strategy`, etc., are defined using SQLAlchemy's `relationship`. This sets up
    the ORM to handle joins and related object access seamlessly.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    Represents a user of the AuraQuant platform.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Core Identity and Credentials
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))

    # Permissions and Status
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)

    # Timestamps (Timezone aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # User Preferences
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    language: Mapped[str] = mapped_column(String(10), default="en")  # ISO 639-1 code
    theme: Mapped[str] = mapped_column(String(10), default="system")  # 'light', 'dark', 'system'

    # Push Notifications
    firebase_device_token: Mapped[Optional[str]] = mapped_column(String(255))

    # Two-Factor Authentication (2FA)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255))  # Encrypted
    is_two_factor_enabled: Mapped[bool] = mapped_column(Boolean(), default=False)

    # --- Relationships ---
    # A single user can have one subscription. (One-to-One)
    subscription: Mapped["Subscription"] = relationship(back_populates="user", cascade="all, delete-orphan")

    # A single user can have multiple API keys. (One-to-Many)
    api_keys: Mapped[List["ApiKey"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # A single user can have multiple payment records. (One-to-Many)
    payments: Mapped[List["Payment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # A single user can create multiple trading strategies. (One-to-Many)
    strategies: Mapped[List["Strategy"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    

    # A user has one specific risk profile. (One-to-One)
    risk_profile: Mapped[Optional["UserRiskProfile"]] = relationship(back_populates="user",
                                                                     cascade="all, delete-orphan")
    published_strategies: Mapped[List["MarketplaceStrategy"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )
    paper_account: Mapped[Optional["PaperAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")


    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', is_superuser={self.is_superuser})>"