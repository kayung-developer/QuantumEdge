"""
AuraQuant - Pydantic Schemas for the UserRiskProfile Model
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Base Schema ---
# Contains all the common attributes for a user's risk profile.
class UserRiskProfileBase(BaseModel):
    max_open_positions: Optional[int] = Field(None, ge=0, description="Maximum number of concurrent open positions.")
    max_order_value_usd: Optional[float] = Field(None, ge=0, description="Maximum USD value for a single order.")
    max_exposure_per_symbol_usd: Optional[float] = Field(None, ge=0, description="Maximum total USD exposure for any single symbol.")
    max_total_exposure_usd: Optional[float] = Field(None, ge=0, description="Maximum total USD exposure across all positions.")
    max_daily_drawdown_pct: Optional[float] = Field(None, ge=0, le=100, description="Maximum allowed loss in a single day, as a percentage of account balance.")
    max_total_drawdown_pct: Optional[float] = Field(None, ge=0, le=100, description="Maximum allowed loss from the all-time high balance.")
    trading_halted: bool = Field(False, description="A global kill switch for a user. If true, no new trades are allowed.")


# --- Create Schema ---
# Properties to receive on risk profile creation. Requires a user_id.
class UserRiskProfileCreate(UserRiskProfileBase):
    user_id: int


# --- Update Schema ---
# Properties to receive on risk profile update. All fields are optional.
# This allows an admin to modify only specific risk parameters.
class UserRiskProfileUpdate(UserRiskProfileBase):
    pass


# --- Response Schema ---
# This is the public-facing model for a user risk profile.
# It includes database-managed fields like `id` and `user_id`.
class UserRiskProfileInDB(UserRiskProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)