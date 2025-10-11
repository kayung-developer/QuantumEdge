"""
AuraQuant - Pydantic Schemas for the ForgeJob Model
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

from app.models.autotrade import ForgeJobStatus

# --- Base Schema ---
class ForgeJobBase(BaseModel):
    strategy_id: str = Field(..., description="The ID of the strategy to optimize (e.g., 'momentum_crossover').")
    symbol: str = Field(..., max_length=50)
    timeframe: str = Field(..., max_length=10)
    start_date: datetime
    end_date: datetime
    optimization_metric: str = Field(..., description="The metric to maximize (e.g., 'sharpe_ratio', 'net_profit').")


# --- Create Schema ---
# This is the payload the user sends to launch a new Forge job.
class ForgeJobCreate(ForgeJobBase):
    pass


# --- Response Schema ---
# This is the full model returned to the user, showing job status and results.
class ForgeJobInDB(ForgeJobBase):
    id: UUID
    user_id: int
    status: ForgeJobStatus
    best_parameters: Optional[Dict[str, Any]] = None
    best_performance: Optional[Dict[str, Any]] = None
    top_permutations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)