"""
AuraQuant - Pydantic Schemas for Market Data
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SymbolInfo(BaseModel):
    """
    Represents information about a tradable symbol.
    """
    name: str
    description: str
    exchange: Optional[str] = None
    currency_base: str
    currency_profit: str
    volume_min: float
    volume_max: float
    volume_step: float
    trade_contract_size: float

class TickData(BaseModel):
    """
    Represents a single price tick.
    """
    symbol: str
    time: datetime
    bid: float
    ask: float
    last: Optional[float] = None
    volume: Optional[int] = None

class KlineData(BaseModel):
    """
    Represents a single candlestick (OHLCV).
    The `time` field is a Unix timestamp (seconds), compatible with charting libraries.
    """
    time: int = Field(..., description="Unix timestamp (seconds)")
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(..., alias="tick_volume")

    class Config:
        populate_by_name = True # Allows using 'tick_volume' from MT5 data for the 'volume' field.

class MarketStatus(BaseModel):
    """

    Represents the overall market connection status.
    """
    connection_status: str
    server_time: datetime
    account_login: int
    account_balance: float
    account_equity: float
    account_currency: str