"""
AuraQuant - CRUD Operations for the AdaptivePortfolio Model
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.adaptive import AdaptivePortfolio
from app.schemas.adaptive import AdaptivePortfolioCreate, AdaptivePortfolioUpdate


class CRUDAdaptivePortfolio(CRUDBase[AdaptivePortfolio, AdaptivePortfolioCreate, AdaptivePortfolioUpdate]):
    async def create_with_user(self, db: AsyncSession, *, obj_in: AdaptivePortfolioCreate,
                               user_id: int) -> AdaptivePortfolio:
        """
        Creates a new adaptive portfolio and associates it with a user ID.
        """
        db_obj = self.model(**obj_in.model_dump(), user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[AdaptivePortfolio]:
        """
        Retrieves the first adaptive portfolio for a specific user ID.
        In this version, we assume a one-portfolio-per-user limit for simplicity.
        """
        result = await db.execute(
            select(self.model).filter(AdaptivePortfolio.user_id == user_id)
        )
        return result.scalars().first()

    async def get_multi_by_user(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[
        AdaptivePortfolio]:
        """
        Retrieves all adaptive portfolios for a specific user.
        """
        result = await db.execute(
            select(self.model)
            .filter(AdaptivePortfolio.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_active(self, db: AsyncSession) -> List[AdaptivePortfolio]:
        """
        Retrieves all adaptive portfolios across all users that are currently active.
        This is used by the background worker service.
        """
        result = await db.execute(
            select(self.model).filter(AdaptivePortfolio.is_active == True)
        )
        return result.scalars().all()


# Create a single instance
crud_adaptive_portfolio = CRUDAdaptivePortfolio(AdaptivePortfolio)