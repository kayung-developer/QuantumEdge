"""
AuraQuant - CRUD Operations for the Plan Model
"""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate

class CRUDPlan(CRUDBase[Plan, PlanCreate, PlanUpdate]):
    async def get_public_plans(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Plan]:
        """
        Retrieves only the active and public subscription plans.
        """
        result = await db.execute(
            select(self.model)
            .filter(Plan.is_active == True, Plan.is_public == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Create a single instance to be used across the application
crud_plan = CRUDPlan(Plan)