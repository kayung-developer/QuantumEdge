"""
AuraQuant - Pydantic Schemas for the Dashboard
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .market_data import MarketStatus
from .trade import PositionInfo

class PortfolioTimeSeriesData(BaseModel):
    """
    Represents a single data point for the portfolio value over time.
    """
    time: datetime
    value: float

class DashboardSummary(BaseModel):
    """
    Aggregates all necessary data for the main user dashboard.
    """
    market_status: MarketStatus
    open_positions_count: int
    total_profit_loss: float
    recent_positions: List[PositionInfo]
    portfolio_history: List[PortfolioTimeSeriesData]