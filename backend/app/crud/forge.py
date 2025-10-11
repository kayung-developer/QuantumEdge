"""
AuraQuant - CRUD Operations for the ForgeJob Model
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.autotrade import ForgeJob
from app.schemas.forge import ForgeJobCreate
from pydantic import BaseModel


# A ForgeJob is created and then updated internally by the service,
# so we don't need a dedicated Update schema for the API.
class CRUDForgeJob(CRUDBase[ForgeJob, ForgeJobCreate, BaseModel]):

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ForgeJob]:
        """
        Overrides the base get method to work with a UUID primary key.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def update(self, db: AsyncSession, *, db_obj_id: UUID, obj_in: dict) -> Optional[ForgeJob]:
        """
        Custom update method to update a job by its UUID.
        """
        db_obj = await self.get(db, id=db_obj_id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj


# Create a single instance
crud_forge_job = CRUDForgeJob(ForgeJob)