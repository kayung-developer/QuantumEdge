"""
AuraQuant - Pydantic Schemas for the Payment Model
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, AnyHttpUrl

from app.models.payment import PaymentStatus

# --- Base Schema ---
class PaymentBase(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[PaymentStatus] = None
    provider: Optional[str] = None


# --- Create Schema (Internal) ---
class PaymentCreate(PaymentBase):
    user_id: int
    subscription_id: Optional[int] = None
    amount: float
    currency: str
    provider: str
    provider_transaction_id: str


# --- Update Schema (Internal) ---
class PaymentUpdate(BaseModel):
    status: PaymentStatus


# --- Payment Initiation Schemas ---
# Schema for the request to initiate a payment
class PaymentInitiate(BaseModel):
    plan_id: int
    interval: str # 'monthly' or 'yearly'
    provider: str # 'paystack' or 'paypal'
    success_url: AnyHttpUrl
    cancel_url: AnyHttpUrl

# Schema for the response after initiating a payment
class PaymentInitiateResponse(BaseModel):
    provider: str
    authorization_url: AnyHttpUrl
    reference: str


# --- Public Response Schema ---
class Payment(PaymentBase):
    id: int
    user_id: int
    provider_transaction_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)