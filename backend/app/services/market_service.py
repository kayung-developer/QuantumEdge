"""
AuraQuant - Unified Market Service (Complete Implementation)

This service acts as the central, unified entry point for all market data and
trade execution requests across all connected exchanges and brokers.

Its primary responsibility is to abstract away the specifics of each exchange.
The rest of the application (e.g., API endpoints, trading logic bots) will
interact with this service, simply specifying which exchange they want to
target for a given action.

This service uses the ConnectionManager to find the appropriate, active exchange
adapter and delegates the request to it, ensuring a clean separation of concerns
and making the entire system highly modular and extensible.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.connections import connection_manager
from app.core.exchange_adapter import ExchangeAdapterProtocol
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo

class UnifiedMarketService:
    """
    A complete and robust service for interacting with any connected exchange.
    """

    def get_adapter(self, exchange_name: str) -> ExchangeAdapterProtocol:
        """
        A robust helper method to retrieve an active adapter.

        This is a critical internal function that ensures any service method
        attempting to perform an action has a valid, connected adapter to work with.

        Args:
            exchange_name: The name of the target exchange (e.g., 'Binance', 'MetaTrader5').

        Returns:
            The active adapter instance.

        Raises:
            ValueError: If the requested exchange is not supported, not configured,
                        or not currently connected.
        """
        adapter = connection_manager.get_adapter(exchange_name)
        if not adapter:
            # Provide a detailed error message for easier debugging.
            all_adapters = connection_manager._adapters.keys()
            active_adapters = [a.exchange_name for a in connection_manager.get_all_active_adapters()]
            error_message = (
                f"No active connection found for exchange: '{exchange_name}'. "
                f"Supported adapters: {list(all_adapters)}. "
                f"Currently active connections: {active_adapters}."
            )
            raise ValueError(error_message)
        return adapter

    # --- Unified Connection & Status Methods ---

    def get_all_active_connections(self) -> List[str]:
        """
        Returns the names of all currently connected and active exchanges.
        """
        return [adapter.exchange_name for adapter in connection_manager.get_all_active_adapters()]

    # --- Unified Market Data Methods ---

    async def get_all_symbols(self, exchange_name: str) -> List[SymbolInfo]:
        """
        Delegates the request to fetch all symbols for a specific exchange.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_all_symbols()

    async def get_symbol_info(self, exchange_name: str, symbol: str) -> Optional[SymbolInfo]:
        """
        Delegates the request to fetch detailed info for a single symbol.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_symbol_info(symbol)

    async def get_latest_tick(self, exchange_name: str, symbol: str) -> Optional[TickData]:
        """
        Delegates the request to fetch the latest price tick.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_latest_tick(symbol)

    async def get_historical_klines(
        self, exchange_name: str, symbol: str, timeframe: str, start_dt: datetime, end_dt: datetime
    ) -> List[KlineData]:
        """
        Delegates the request to fetch historical kline data.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_historical_klines(symbol, timeframe, start_dt, end_dt)

    # --- Unified Trade Execution & Account Methods ---

    async def place_order(self, exchange_name: str, order_request: OrderRequest) -> OrderResult:
        """
        Delegates the request to place a new order on a specific exchange.
        """
        adapter = self.get_adapter(exchange_name)
        # Ensure the order is routed to the correct symbol for the exchange
        # (This is a good place for pre-flight validation if needed)
        if not await adapter.get_symbol_info(order_request.symbol):
             raise ValueError(f"Symbol '{order_request.symbol}' does not exist on exchange '{exchange_name}'.")
        return await adapter.place_order(order_request)

    async def cancel_order(self, exchange_name: str, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Delegates the request to cancel an order.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.cancel_order(order_id, symbol)

    async def get_open_positions(self, exchange_name: str) -> List[PositionInfo]:
        """
        Delegates the request to fetch all open positions from an exchange account.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_open_positions()

    async def get_trade_history(
        self, exchange_name: str, start_date: datetime, end_date: datetime
    ) -> List[TradeHistoryInfo]:
        """
        Delegates the request to fetch trade history from an exchange account.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_trade_history(start_date, end_date)

    async def get_account_balance(self, exchange_name: str) -> Dict[str, Any]:
        """
        Delegates the request to fetch account balance and equity information.
        """
        adapter = self.get_adapter(exchange_name)
        return await adapter.get_account_balance()


# Create a single, globally accessible instance of the service.
# This instance will be imported and used by the API endpoints.
unified_market_service = UnifiedMarketService()