"""
AuraQuant - Core Exchange Adapter Protocol

This module defines the abstract interface (Protocol) that all exchange and broker
adapters must implement. This ensures that the core application logic can interact
with any trading venue in a consistent, standardized way.

This abstraction is the key to building a true multi-market system.
"""
from typing import Protocol, List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ExchangeAdapterProtocol(Protocol):
    """
    A protocol defining the standard interface for all exchange/broker adapters.
    """
    exchange_name: str

    # --- Connection Management ---
    async def connect(self):
        """
        Establish and initialize the connection to the exchange/broker.
        """
        ...

    async def disconnect(self):
        """
        Gracefully close the connection.
        """
        ...

    def get_status(self) -> ConnectionStatus:
        """
        Return the current status of the connection.
        """
        ...

    # --- Market Data ---
    async def get_all_symbols(self) -> List[SymbolInfo]:
        """
        Fetch information for all available symbols on the exchange.
        """
        ...

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Fetch detailed information for a single symbol.
        """
        ...

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        """
        Fetch the most recent tick data for a given symbol.
        """
        ...

    async def get_historical_klines(
            self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime
    ) -> List[KlineData]:
        """
        Fetch historical candlestick (OHLCV) data for a given symbol and date range.
        """
        ...

    # --- Trade Execution ---
    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        """
        Places a new trade order.
        """
        ...

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancels an open order.
        """
        ...

    async def get_open_positions(self) -> List[PositionInfo]:
        """
        Retrieves all currently open trading positions for the account.
        """
        ...

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        """
        Retrieves trade history (deals/fills) for a given date range.
        """
        ...

    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Retrieves the account balance and equity information.
        """
        ...