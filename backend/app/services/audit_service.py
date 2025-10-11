"""
AuraQuant - Audit Logging Service (Complete Implementation)

This service provides a centralized, high-level interface for creating audit log
entries. It acts as an abstraction layer over the CRUD operations, ensuring that
any part of the application (e.g., login endpoints, risk engine, order orchestrator)
can log significant events in a consistent and straightforward manner.

The primary design principle is simplicity and reliability. This service's only
job is to persist audit events, forming an immutable log of system and user actions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from app.crud.audit import crud_audit_log
from app.schemas.audit import AuditLogCreate
from app.models.audit import AuditAction

class AuditService:
    """
    A service dedicated to creating and managing audit trail logs.
    """

    async def log(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[int],
        action: AuditAction,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Creates and persists a new audit log entry.

        This is the core method of the service and is designed to be called
        as a simple one-liner from other services.

        Args:
            db: The active SQLAlchemy async session.
            user_id: The ID of the user performing the action. Can be None for system events.
            action: The type of action being performed, from the AuditAction enum.
            details: A human-readable string describing the event.
            metadata: A dictionary of structured data related to the event for
                      detailed analysis (e.g., IP address, order details, changed fields).
        """
        # Create the Pydantic schema object for the new log entry.
        log_entry = AuditLogCreate(
            user_id=user_id,
            action=action,
            details=details,
            metadata=metadata or {} # Ensure metadata is at least an empty dict
        )

        # Use the dedicated CRUD object to create the record in the database.
        # This operation is fire-and-forget from the perspective of the calling service.
        await crud_audit_log.create_log(db, obj_in=log_entry)

# Create a single, globally accessible instance of the service.
audit_service = AuditService()