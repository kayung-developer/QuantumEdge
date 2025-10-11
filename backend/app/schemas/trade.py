"""
AuraQuant - Pydantic Schemas for Trade Execution
"""
from typing import Optional, List
from pydantic import BaseModel, Field, conint
from enum import Enum
from datetime import datetime


class OrderType(str, Enum):
    """
    Enum for different order types.
    Matches MetaTrader 5's ORDER_TYPE_* constants.
    """
    BUY = "buy"
    SELL = "sell"
    BUY_LIMIT = "buy_limit"
    SELL_LIMIT = "sell_limit"
    BUY_STOP = "buy_stop"
    SELL_STOP = "sell_stop"


class OrderAction(str, Enum):
    """
    Enum for the action to be taken on an order.
    Matches MetaTrader 5's TRADE_ACTION_* constants.
    """
    DEAL = "deal"
    PENDING = "pending"
    SLTP = "sltp"
    MODIFY = "modify"
    REMOVE = "remove"


class OrderRequest(BaseModel):
    """
    Schema for a new trade order request from the client.
    """
    symbol: str = Field(..., description="The financial instrument to trade")
    volume: float = Field(..., gt=0, description="Trade volume or lot size")
    type: OrderType
    price: Optional[float] = Field(None, description="Entry price for pending orders")
    sl: Optional[float] = Field(None, description="Stop Loss price")
    tp: Optional[float] = Field(None, description="Take Profit price")
    deviation: int = Field(10, description="Deviation for price execution")
    magic: int = Field(234000, description="Magic number for the order")
    comment: str = Field("AuraQuant Execution", description="Order comment")


class OrderResult(BaseModel):
    """
    Schema for the result of a trade request, returned from MT5.
    """
    retcode: int = Field(..., description="Return code from the trade server")
    deal: int = Field(..., description="Deal ticket")
    order: int = Field(..., description="Order ticket")
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_message: str


class PositionInfo(BaseModel):
    """
    Schema for an open trading position.
    """
    ticket: int
    symbol: str
    type: str
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    profit: float
    time: datetime
    magic: int
    comment: str


class TradeHistoryInfo(BaseModel):
    """
    Schema for a historical trade deal.
    """
    ticket: int
    order: int
    symbol: str
    type: str
    entry: str
    volume: float
    price: float
    profit: float
    time: datetime
    magic: int
    comment: str