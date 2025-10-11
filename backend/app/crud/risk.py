"""
AuraQuant - CRUD Operations for the UserRiskProfile Model
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.risk import UserRiskProfile
from app.models.user import User
from app.schemas.risk import UserRiskProfileCreate, UserRiskProfileUpdate

class CRUDUserRiskProfile(CRUDBase[UserRiskProfile, UserRiskProfileCreate, UserRiskProfileUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[UserRiskProfile]:
        """
        Retrieves a risk profile for a specific user ID.
        """
        result = await db.execute(
            select(self.model).filter(UserRiskProfile.user_id == user_id)
        )
        return result.scalars().first()

    async def get_by_user_id_with_user(self, db: AsyncSession, *, user_id: int) -> Optional[UserRiskProfile]:
        """
        Retrieves a risk profile for a specific user ID, eagerly loading the
        related User object.
        """
        result = await db.execute(
            select(self.model)
            .options(selectinload(UserRiskProfile.user))
            .filter(UserRiskProfile.user_id == user_id)
        )
        return result.scalars().first()

# Create a single instance to be used across the application
crud_risk_profile = CRUDUserRiskProfile(UserRiskProfile)