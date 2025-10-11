"""
AuraQuant - CRUD Operations for the SentimentData Model
"""
from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sentiment import SentimentData
from app.schemas.sentiment import SentimentDataCreate
from pydantic import BaseModel


# SentimentData is write-once, so we don't need an Update schema.
class CRUDSentimentData(CRUDBase[SentimentData, SentimentDataCreate, BaseModel]):

    async def get_by_symbol_and_daterange(
            self,
            db: AsyncSession,
            *,
            symbol: str,
            start_date: datetime,
            end_date: datetime,
            limit: int = 100
    ) -> List[SentimentData]:
        """
        Retrieves historical sentiment data for a specific symbol within a date range,
        ordered by the most recent first.

        Args:
            db: The SQLAlchemy async session.
            symbol: The trading symbol to query for (e.g., 'BTCUSDT').
            start_date: The start of the time window.
            end_date: The end of the time window.
            limit: The maximum number of records to return.

        Returns:
            A list of SentimentData objects.
        """
        result = await db.execute(
            select(self.model)
            .filter(
                SentimentData.symbol == symbol,
                SentimentData.timestamp >= start_date,
                SentimentData.timestamp <= end_date
            )
            .order_by(SentimentData.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Create a single instance to be used across the application.
crud_sentiment = CRUDSentimentData(SentimentData)