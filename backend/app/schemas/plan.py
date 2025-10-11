"""
AuraQuant - Pydantic Schemas for the Plan Model
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# --- Base Schema ---
# Contains common attributes for a subscription plan.
class PlanBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    currency: Optional[str] = "USD"
    features: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True
    is_public: Optional[bool] = True


# --- Create Schema ---
# Properties to receive on plan creation.
class PlanCreate(PlanBase):
    name: str
    price_monthly: float
    price_yearly: float
    features: Dict[str, Any]


# --- Update Schema ---
# Properties to receive on plan update. All fields are optional.
class PlanUpdate(PlanBase):
    pass


# --- Response Schema ---
# This is the public-facing model for a plan.
# It includes database-managed fields like `id`.
class Plan(PlanBase):
    id: int

    model_config = ConfigDict(from_attributes=True)