"""
AuraQuant - Pydantic Schemas for Backtesting
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class BacktestRequest(BaseModel):
    strategy_id: str # The key from STRATEGY_REGISTRY
    symbol: str
    exchange: str
    timeframe: str
    start_date: str # ISO format string e.g., "2023-01-01"
    end_date: str
    parameters: Dict[str, Any]

class StrategyInfo(BaseModel):
    id: str
    name: str
    description: str
    default_params: Dict[str, Any]

class BacktestPerformanceResults(BaseModel):
    net_profit: float
    total_trades: int
    win_rate_pct: float
    profit_factor: float
    max_drawdown_pct: float
    sharpe_ratio: float
    # ... Add all other metrics from the backtester's output

class BacktestResponse(BaseModel):
    strategy_name: str
    symbol: str
    timeframe: str
    performance: BacktestPerformanceResults
    equity_curve: Dict[str, float]
    trades: List[Dict[str, Any]]
    parameters: Dict[str, Any]