"""
AuraQuant - Trading Account Credentials Database Model
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, DateTime, func, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.core.security import fernet  # We will add Fernet encryption to security.py


class TradingAccount(Base):
    """
    Stores encrypted credentials for a user's connection to an external
    exchange or broker. This allows for multi-account support.
    """
    __tablename__ = "trading_accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    exchange_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., 'Binance', 'MT5', 'LMAX'

    # --- Encrypted Credentials ---
    # We never store API keys or passwords in plain text. They are encrypted
    # using a secret key ONLY known to the server application.
    encrypted_credentials: Mapped[bytes] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_read_only: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    user: Mapped["User"] = relationship()

    @property
    def credentials(self) -> dict:
        """Decrypts the credentials on-the-fly when accessed."""
        return json.loads(fernet.decrypt(self.encrypted_credentials))

    @credentials.setter
    def credentials(self, value: dict):
        """Encrypts the credentials when being set."""
        self.encrypted_credentials = fernet.encrypt(json.dumps(value).encode())





# ... (pwd_context, reusable_oauth2)



# ... (get_password_hash, verify_password, create_access_token)