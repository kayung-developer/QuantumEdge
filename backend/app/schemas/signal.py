"""
AuraQuant - Pydantic Schemas for the AISignal Model
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

from app.models.signal import SignalStatus

# --- Base Schema ---
class AISignalBase(BaseModel):
    model_name: str
    model_version: str
    exchange: str
    symbol: str
    timeframe: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence_score: float
    expires_at: datetime
    rationale: Optional[str] = None
    signal_metadata: Optional[Dict[str, Any]] = None


# --- Create Schema (Internal) ---
# Used by the SignalService to create a new signal record.
class SignalCreate(AISignalBase):
    user_id: int


# --- Action Schema ---
# The payload a user sends to approve or reject a signal.
class SignalAction(BaseModel):
    action_type: str = Field(..., pattern="^(APPROVE|REJECT)$", description="'APPROVE' or 'REJECT'")
    # Future enhancement: Allow modifying parameters on approval
    # modifications: Optional[Dict[str, Any]] = None


# --- Response Schema ---
# The full public model for an AI signal returned by the API.
class AISignalInDB(AISignalBase):
    id: UUID
    user_id: int
    status: SignalStatus
    generated_at: datetime
    actioned_at: Optional[datetime] = None
    orchestrated_order_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)