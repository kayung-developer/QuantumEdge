"""
AuraQuant - Pydantic Schemas for the Subscription Model
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.subscription import SubscriptionStatus
from .plan import Plan  # Import the public Plan schema

# --- Base Schema ---
class SubscriptionBase(BaseModel):
    plan_id: Optional[int] = None
    status: Optional[SubscriptionStatus] = None
    provider: Optional[str] = None
    provider_subscription_id: Optional[str] = None


# --- Create Schema ---
# Note: Subscriptions are usually created internally by the payment system,
# so a public create schema might not be needed. This is for internal use.
class SubscriptionCreate(SubscriptionBase):
    user_id: int
    plan_id: int
    current_period_end: datetime


# --- Update Schema ---
class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    status: Optional[SubscriptionStatus] = None
    end_date: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    provider_subscription_id: Optional[str] = None


# --- Response Schema ---
# This is the public model returned to the user. It includes the full plan details.
class Subscription(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    current_period_start: datetime
    current_period_end: datetime
    plan: Plan # Nested plan details

    model_config = ConfigDict(from_attributes=True)