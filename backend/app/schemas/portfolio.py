"""
AuraQuant - Pydantic Schemas for Portfolio Intelligence API
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from .order import Order # Import the existing Order schema

# --- Schemas for /analysis endpoint ---
class AssetCorrelation(BaseModel):
    symbol: str
    correlation: Dict[str, float]

class PortfolioAnalysisResponse(BaseModel):
    total_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    asset_correlation_matrix: List[AssetCorrelation]

# --- Schemas for /optimize endpoint ---
class OptimizationResponse(BaseModel):
    optimal_weights: Dict[str, float]
    expected_annual_return_pct: float
    annual_volatility_pct: float
    sharpe_ratio: float

# --- Schemas for /forensics endpoint ---
class TradePerformanceMetrics(BaseModel):
    profit_usd: float
    return_on_notional_pct: float
    duration_seconds: float
    max_favorable_excursion_usd: float # MFE
    max_adverse_excursion_usd: float # MAE

class MarketContext(BaseModel):
    rsi_14: Optional[float]
    macd_histogram: Optional[float]
    volume: Optional[float]
    # In a more advanced system, you could add more context here
    # e.g., news_sentiment_score, volatility_regime

class TradeForensicsResponse(BaseModel):
    order: Order
    performance: TradePerformanceMetrics
    market_context_at_entry: MarketContext