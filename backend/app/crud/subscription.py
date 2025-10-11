"""
AuraQuant - CRUD Operations for the Subscription Model
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from app.crud.base import CRUDBase
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.models.user import User


class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    async def get_active_by_user_id(
            self, db: AsyncSession, *, user_id: int
    ) -> Optional[Subscription]:
        """
        Get the active or trialing subscription for a specific user.
        Loads the related Plan details as well.
        """
        result = await db.execute(
            select(self.model)
            .options(selectinload(Subscription.plan))
            .filter(
                Subscription.user_id == user_id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
            )
        )
        return result.scalars().first()

    async def create_with_user(
            self, db: AsyncSession, *, obj_in: SubscriptionCreate, user: User
    ) -> Subscription:
        """
        Create a new subscription and associate it with a user.
        """
        db_obj = self.model(**obj_in.model_dump(), user=user)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Create a single instance
crud_subscription = CRUDSubscription(Subscription)