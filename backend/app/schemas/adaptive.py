"""
AuraQuant - Pydantic Schemas for the AdaptivePortfolio Model
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

# --- Base Schema ---
# Contains common, user-configurable attributes for an adaptive portfolio.
class AdaptivePortfolioBase(BaseModel):
    name: str = Field(..., max_length=100, description="A user-friendly name for the portfolio.")
    symbol: str = Field(..., max_length=50, description="The target symbol for this adaptive portfolio (e.g., 'BTCUSDT').")
    regime_strategy_map: Dict[str, Any] = Field(
        ...,
        description="The core mapping of regime ID (as string) to strategy ID (string). e.g., {'0': 'momentum_crossover'}"
    )

# --- Create Schema ---
# Properties to receive on adaptive portfolio creation.
class AdaptivePortfolioCreate(AdaptivePortfolioBase):
    pass

# --- Update Schema ---
# Properties to receive on update. All are optional.
# This allows for updating just the name, the map, or its active status.
class AdaptivePortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    regime_strategy_map: Optional[Dict[str, Any]] = None

# --- Response Schema ---
# This is the full public-facing model, including database-managed fields.
class AdaptivePortfolioInDB(AdaptivePortfolioBase):
    id: int
    user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)