"""
AuraQuant - CRUD Operations for the AuditLog Model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogCreate
from pydantic import BaseModel


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, BaseModel]):  # No Update schema
    """
    Specialized CRUD class for Audit Logs.
    The primary operation is creating new log entries.
    """

    async def create(self, db: AsyncSession, *, obj_in: AuditLogCreate) -> AuditLog:
        """
        Creates a new audit log entry in the database.
        This is the core method for this class.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_log(self, db: AsyncSession, *, obj_in: AuditLogCreate) -> AuditLog:
        """
        A semantic alias for the `create` method for clearer service-layer code.
        Example: `audit_service.log(...)` which calls `crud_audit_log.create_log(...)`
        """
        return await self.create(db, obj_in=obj_in)


# Create a single instance to be used across the application
crud_audit_log = CRUDAuditLog(AuditLog)