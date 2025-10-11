"""
AuraQuant - Pydantic Schemas for the AuditLog Model
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.audit import AuditAction

# --- Base Schema ---
class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    action: AuditAction
    details: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None


# --- Create Schema ---
# This is the primary schema used by services to log a new event.
class AuditLogCreate(AuditLogBase):
    pass


# --- Response Schema ---
# This schema represents an audit log entry as returned from the API,
# for example, in an admin panel for viewing audit trails.
class AuditLogInDB(AuditLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)