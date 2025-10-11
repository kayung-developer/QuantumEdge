"""
AuraQuant - Pydantic Schemas for Walk-Forward Optimization
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .backtest import BacktestPerformanceResults


class WalkForwardChunkResult(BaseModel):
    """Represents the results for a single walk-forward period."""
    in_sample_start: datetime
    in_sample_end: datetime
    out_of_sample_start: datetime
    out_of_sample_end: datetime
    optimal_parameters: Dict[str, Any]
    in_sample_performance: BacktestPerformanceResults
    out_of_sample_performance: BacktestPerformanceResults


class WalkForwardJobCreate(BaseModel):
    strategy_id: str
    symbol: str
    exchange: str
    timeframe: str
    start_date: str
    end_date: str

    # Walk-Forward Specific Parameters
    training_period_days: int = Field(..., gt=0, description="Length of the in-sample (optimization) period in days.")
    testing_period_days: int = Field(..., gt=0, description="Length of the out-of-sample (validation) period in days.")
    optimization_metric: str = Field("sharpe_ratio", description="The metric to optimize during the in-sample phase.")


class WalkForwardJobInDB(BaseModel):
    id: str  # Will be the Celery Task ID
    status: str  # PENDING, RUNNING, SUCCESS, FAILURE
    user_id: int
    config: WalkForwardJobCreate
    results: Optional[List[WalkForwardChunkResult]] = None
    overall_performance: Optional[BacktestPerformanceResults] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True