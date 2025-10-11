"""
AuraQuant - Pydantic Schemas for Orchestrated Orders (with Paper Trading)
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field
from app.models.order import OrderStatus

class AlgoParams(BaseModel):
    """Parameters specific to algorithmic orders."""
    duration_minutes: int = Field(..., gt=0, description="Total duration for the TWAP execution in minutes.")
    num_children: int = Field(..., gt=0, description="Number of smaller orders to split the parent into.")

class OrderCreate(BaseModel):
    """
    Schema for a client's request to create a new orchestrated order.
    Can be a live trade or a paper trade.
    """
    exchange: str = Field(..., description="Target exchange name (e.g., 'Binance', 'MetaTrader5').")
    symbol: str
    order_type: str # 'MARKET' or 'LIMIT'
    side: str # 'BUY' or 'SELL'
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, description="Required for LIMIT orders")

    # --- NEW: Paper Trading Flag ---
    is_paper_trade: bool = Field(False, description="If true, the order will be simulated against live market data instead of being sent to an exchange.")

    # Algorithmic trading parameters
    is_algorithmic: bool = False
    algo_params: Optional[AlgoParams] = None

    class Config:
        json_schema_extra = {
            "example_live": {
                "exchange": "Binance",
                "symbol": "BTCUSDT",
                "order_type": "LIMIT",
                "side": "BUY",
                "quantity": 0.01,
                "price": 50000.0,
                "is_paper_trade": False
            },
            "example_paper": {
                "exchange": "Binance",
                "symbol": "ETHUSDT",
                "order_type": "MARKET",
                "side": "SELL",
                "quantity": 0.5,
                "is_paper_trade": True
            }
        }

class Order(BaseModel):
    """
    The full public schema for an orchestrated order, returned by the API.
    """
    id: UUID
    user_id: int
    exchange: str
    symbol: str
    exchange_order_id: Optional[str] = None
    order_type: str
    side: str
    quantity_requested: float
    price: Optional[float] = None
    status: OrderStatus
    quantity_filled: float
    average_fill_price: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    is_paper_trade: bool # Include the flag in the response

    class Config:
        from_attributes = True