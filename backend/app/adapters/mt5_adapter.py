"""
AuraQuant - MetaTrader 5 Exchange Adapter (Complete Implementation)
"""
import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any

import MetaTrader5 as mt5

from app.core.config import settings
from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo, OrderType

class MT5Adapter(ExchangeAdapterProtocol):
    exchange_name: str = "MetaTrader5"
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    _loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return self._loop

    async def _run_blocking(self, func, *args, **kwargs):
        """Helper to run blocking MT5 calls in a thread pool."""
        if self.get_status() != ConnectionStatus.CONNECTED:
            raise ConnectionError("MetaTrader 5 is not connected.")
        return await self._get_loop().run_in_executor(None, lambda: func(*args, **kwargs))

    async def connect(self):
        self._status = ConnectionStatus.CONNECTING
        if not all([settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER]):
            self._status = ConnectionStatus.ERROR
            raise ConnectionError("MT5 credentials are not fully configured.")

        initialized = await self._get_loop().run_in_executor(
            None, mt5.initialize,
            settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER
        )

        if not initialized:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError(f"MT5 initialization failed. Error: {mt5.last_error()}")

        self._status = ConnectionStatus.CONNECTED

    async def disconnect(self):
        if self._status == ConnectionStatus.CONNECTED:
            await self._run_blocking(mt5.shutdown)
            self._status = ConnectionStatus.DISCONNECTED

    def get_status(self) -> ConnectionStatus:
        return self._status

    async def get_all_symbols(self) -> List[SymbolInfo]:
        symbols = await self._run_blocking(mt5.symbols_get)
        if not symbols: return []

        tasks = [self.get_symbol_info(s.name) for s in symbols]
        results = await asyncio.gather(*tasks)
        return [res for res in results if res is not None]

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        info = await self._run_blocking(mt5.symbol_info, symbol)
        if not info: return None
        return SymbolInfo(
            name=info.name, description=info.description,
            exchange="MT5", currency_base=info.currency_base,
            currency_profit=info.currency_profit,
            volume_min=info.volume_min, volume_max=info.volume_max,
            volume_step=info.volume_step, trade_contract_size=info.trade_contract_size
        )

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        tick = await self._run_blocking(mt5.symbol_info_tick, symbol)
        if not tick: return None
        return TickData(
            symbol=symbol, time=datetime.fromtimestamp(tick.time),
            bid=tick.bid, ask=tick.ask, last=tick.last, volume=int(tick.volume)
        )

    async def get_historical_klines(
        self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime
    ) -> List[KlineData]:
        timeframe_map = {
            "1M": mt5.TIMEFRAME_M1, "5M": mt5.TIMEFRAME_M5, "15M": mt5.TIMEFRAME_M15,
            "30M": mt5.TIMEFRAME_M30, "1H": mt5.TIMEFRAME_H1, "4H": mt5.TIMEFRAME_H4,
            "1D": mt5.TIMEFRAME_D1, "1W": mt5.TIMEFRAME_W1, "1MN": mt5.TIMEFRAME_MN1
        }
        timeframe = timeframe_map.get(timeframe_str.upper())
        if timeframe is None:
            raise ValueError(f"Unsupported timeframe: {timeframe_str}")

        rates = await self._run_blocking(mt5.copy_rates_range, symbol, timeframe, start_dt, end_dt)
        if rates is None or len(rates) == 0:
            return []

        df = pd.DataFrame(rates)
        return [KlineData(**row) for row in df.to_dict('records')]

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        symbol_info = await self._run_blocking(mt5.symbol_info, order_request.symbol)
        if symbol_info is None: raise ValueError(f"Symbol {order_request.symbol} not found.")

        fill_policy_map = {
            mt5.SYMBOL_FILLING_FOK: mt5.ORDER_FILLING_FOK,
            mt5.SYMBOL_FILLING_IOC: mt5.ORDER_FILLING_IOC,
            mt5.SYMBOL_FILLING_RETURN: mt5.ORDER_FILLING_RETURN,
        }
        fill_policy = fill_policy_map.get(symbol_info.filling_mode, mt5.ORDER_FILLING_FOK)

        mt5_order_type_map = {
            OrderType.BUY: mt5.ORDER_TYPE_BUY, OrderType.SELL: mt5.ORDER_TYPE_SELL,
            OrderType.BUY_LIMIT: mt5.ORDER_TYPE_BUY_LIMIT, OrderType.SELL_LIMIT: mt5.ORDER_TYPE_SELL_LIMIT,
            OrderType.BUY_STOP: mt5.ORDER_TYPE_BUY_STOP, OrderType.SELL_STOP: mt5.ORDER_TYPE_SELL_STOP,
        }
        mt5_order_type = mt5_order_type_map[order_request.type]

        tick = await self._run_blocking(mt5.symbol_info_tick, order_request.symbol)
        price = 0.0
        if order_request.type == OrderType.BUY: price = tick.ask
        elif order_request.type == OrderType.SELL: price = tick.bid
        else: price = order_request.price

        if price is None or price == 0.0:
            raise ValueError("Invalid price for order execution.")

        request = {
            "action": mt5.TRADE_ACTION_DEAL, "symbol": order_request.symbol, "volume": order_request.volume,
            "type": mt5_order_type, "price": price, "sl": order_request.sl or 0.0,
            "tp": order_request.tp or 0.0, "deviation": order_request.deviation, "magic": order_request.magic,
            "comment": order_request.comment, "type_time": mt5.ORDER_TIME_GTC, "type_filling": fill_policy,
        }

        result = await self._run_blocking(mt5.order_send, request)
        if result is None:
            raise ConnectionAbortedError(f"Order send failed, no result. MT5 Error: {mt5.last_error()}")

        return OrderResult(**result._asdict(), retcode_message=result.comment)

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": int(order_id),
        }
        result = await self._run_blocking(mt5.order_send, request)
        if result is None:
            raise ConnectionAbortedError(f"Order cancel failed. MT5 Error: {mt5.last_error()}")

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {"status": "success", "message": result.comment, "details": result._asdict()}
        else:
            raise ValueError(f"Failed to cancel order: {result.comment}")

    async def get_open_positions(self) -> List[PositionInfo]:
        positions = await self._run_blocking(mt5.positions_get)
        if positions is None: return []

        return [PositionInfo(
            ticket=pos.ticket, symbol=pos.symbol, type="BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
            volume=pos.volume, price_open=pos.price_open, price_current=pos.price_current,
            sl=pos.sl, tp=pos.tp, profit=pos.profit, time=pos.time,
            magic=pos.magic, comment=pos.comment
        ) for pos in positions]

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        deals = await self._run_blocking(mt5.history_deals_get, start_date, end_date)
        if deals is None: return []

        return [TradeHistoryInfo(
            ticket=deal.ticket, order=deal.order, symbol=deal.symbol,
            type="BUY" if deal.type == mt5.ORDER_TYPE_BUY else "SELL",
            entry="IN" if deal.entry == mt5.DEAL_ENTRY_IN else "OUT",
            volume=deal.volume, price=deal.price, profit=deal.profit,
            time=deal.time, magic=deal.magic, comment=deal.comment
        ) for deal in deals]

    async def get_account_balance(self) -> Dict[str, Any]:
        info = await self._run_blocking(mt5.account_info)
        if not info:
            raise ValueError("Could not retrieve account info from MT5.")
        return {
            "balance": info.balance,
            "equity": info.equity,
            "profit": info.profit,
            "currency": info.currency,
            "leverage": info.leverage,
        }