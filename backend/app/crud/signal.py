"""
AuraQuant - CRUD Operations for the AISignal Model
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.signal import AISignal, SignalStatus
from app.schemas.signal import SignalCreate
from pydantic import BaseModel

# An AISignal is not updated via a generic API schema.
class CRUDSignal(CRUDBase[AISignal, SignalCreate, BaseModel]):

    async def get(self, db: AsyncSession, id: UUID) -> Optional[AISignal]:
        """
        Overrides the base get method to work with a UUID primary key.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_by_status_for_user(
        self, db: AsyncSession, *, user_id: int, status: SignalStatus
    ) -> List[AISignal]:
        """
        Retrieves all signals for a specific user that are in a given status.
        This is primarily used to fetch 'GENERATED' signals for the user's dashboard.
        """
        result = await db.execute(
            select(self.model)
            .filter(AISignal.user_id == user_id, AISignal.status == status)
            .order_by(AISignal.generated_at.desc())
        )
        return result.scalars().all()

# Create a single instance
crud_signal = CRUDSignal(AISignal)