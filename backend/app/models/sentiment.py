"""
AuraQuant - Database Model for Sentiment Scores
"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SentimentData(Base):
    """
    Stores historical sentiment scores for a given symbol.
    """
    __tablename__ = "sentiment_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String(20))

    # Context from the source
    source: Mapped[str] = mapped_column(String(100))
    headline: Mapped[str] = mapped_column(String(512))

    def __repr__(self):
        return f"<SentimentData(symbol='{self.symbol}', score={self.sentiment_score:.2f})>"