"""
AuraQuant - Smart Order Router (SOR) Service
"""
import asyncio
from typing import List, Dict, Optional, Tuple

from app.core.connections import connection_manager
from app.schemas.market_data import TickData


class SmartOrderRouterService:
    """
    A service that determines the optimal execution venue for a trade.
    """

    async def get_best_quote(self, symbol: str, side: str) -> Optional[Tuple[str, float]]:
        """
        Finds the best price for a trade across all active exchanges.

        This is the core logic of the SOR. It concurrently fetches the latest tick
        data from every connected adapter that supports the given symbol and
        compares their prices to find the optimal venue.

        Args:
            symbol: The trading symbol (e.g., 'BTCUSDT').
            side: The side of the trade ('BUY' or 'SELL').

        Returns:
            A tuple containing the name of the best exchange and the best price,
            or None if the symbol is not found on any active exchange.
        """
        active_adapters = connection_manager.get_all_active_adapters()

        # Concurrently fetch ticks from all adapters that might have the symbol
        tick_tasks = [adapter.get_latest_tick(symbol) for adapter in active_adapters]
        results = await asyncio.gather(*tick_tasks, return_exceptions=True)

        best_price = None
        best_exchange = None

        for i, result in enumerate(results):
            if isinstance(result, TickData):
                exchange_name = active_adapters[i].exchange_name

                if side.upper() == 'BUY':
                    # For a BUY order, we want the lowest ASK price.
                    price = result.ask
                    if best_price is None or price < best_price:
                        best_price = price
                        best_exchange = exchange_name

                elif side.upper() == 'SELL':
                    # For a SELL order, we want the highest BID price.
                    price = result.bid
                    if best_price is None or price > best_price:
                        best_price = price
                        best_exchange = exchange_name

        if best_exchange and best_price:
            return best_exchange, best_price

        return None

    async def generate_execution_plan(
            self, symbol: str, side: str, quantity: float
    ) -> List[Dict[str, any]]:
        """
        Generates a plan for how to execute a total quantity.

        For now, this is a simple plan: send 100% of the order to the exchange
        with the best price.

        A more advanced SOR would split the order across multiple exchanges based
        on liquidity (order book depth), fees, and latency. This implementation
        provides the architectural foundation for that complexity.

        Returns:
            A list of "route legs", where each leg is a dictionary specifying
            the exchange, quantity, and justification.
        """
        best_quote = await self.get_best_quote(symbol, side)

        if not best_quote:
            raise ValueError(f"Could not find a market for symbol '{symbol}' on any active exchange.")

        best_exchange, best_price = best_quote

        print(f"SOR Decision: Best price for {side} {symbol} is {best_price} on {best_exchange}")

        # Simple plan: route 100% to the best venue
        execution_plan = [
            {
                "exchange": best_exchange,
                "quantity_pct": 1.0,  # 100% of the order
                "quantity": quantity,
                "justification": f"Best price ({best_price}) found on this venue."
            }
        ]
        return execution_plan


# Create a single instance
sor_service = SmartOrderRouterService()