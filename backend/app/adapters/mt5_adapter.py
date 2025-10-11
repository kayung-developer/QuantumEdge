"""
AuraQuant - MetaTrader 5 Exchange Adapter (Definitive Complete Cross-Platform Implementation)

This version uses the pure Python `mt5-linux` library. This library re-implements the
MT5 protocol and has NO dependency on the official MetaQuotes library, making it
truly cross-platform and compatible with any Linux/Docker environment.
All methods from the ExchangeAdapterProtocol are fully implemented.
"""
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from mt5linux import MT5, TimeFrame, OrderType as MT5OrderType, Order as MT5Order, Deal, Position

from app.core.config import settings
from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo, OrderType as AuraOrderType

class MT5Adapter(ExchangeAdapterProtocol):
    exchange_name: str = "MetaTrader5"
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    
    def __init__(self):
        login = int(settings.MT5_LOGIN) if settings.MT5_LOGIN else None
        
        # NOTE: The mt5-linux library requires a bridge script running on the same
        # Windows machine as the MT5 terminal. This host/port points to that bridge.
        self.host = '127.0.0.1' 
        self.port = 5000      
        
        if not all([login, settings.MT5_PASSWORD, settings.MT5_SERVER]):
            self.client = None
            return
            
        self.client = MT5(
            host=self.host,
            port=self.port,
            login=login,
            password=settings.MT5_PASSWORD,
            server=settings.MT5_SERVER,
            timeout=5000 # 5 seconds
        )
        self._loop = None

    def _get_loop(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return self._loop

    async def _run_blocking(self, func, *args, **kwargs):
        """Helper to run blocking library calls in a thread pool executor."""
        return await self._get_loop().run_in_executor(None, lambda: func(*args, **kwargs))

    async def connect(self):
        if not self.client:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError("MT5 credentials are not configured, cannot connect.")
            
        self._status = ConnectionStatus.CONNECTING
        try:
            await self._run_blocking(self.client.connect)
            self._status = ConnectionStatus.CONNECTED
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError(f"MT5 connection failed using mt5-linux: {e}")

    async def disconnect(self):
        if self.client and self.get_status() == ConnectionStatus.CONNECTED:
            await self._run_blocking(self.client.disconnect)
        self._status = ConnectionStatus.DISCONNECTED

    def get_status(self) -> ConnectionStatus:
        return self._status
        
    def _map_aura_order_type_to_mt5(self, order_type: AuraOrderType) -> MT5OrderType:
        return MT5OrderType[order_type.name]

    def _map_timeframe_to_mt5(self, timeframe_str: str) -> TimeFrame:
        try:
            return TimeFrame[timeframe_str.upper()]
        except KeyError:
            raise ValueError(f"Unsupported timeframe for MT5: {timeframe_str}")

    async def get_all_symbols(self) -> List[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        symbols_raw = await self._run_blocking(self.client.get_symbols)
        return [SymbolInfo(
                name=s.name, description=s.description, exchange=self.exchange_name,
                currency_base=s.base_currency, currency_profit=s.profit_currency,
                volume_min=s.volume_min, volume_max=s.volume_max,
                volume_step=s.volume_step, trade_contract_size=s.contract_size
            ) for s in symbols_raw]

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        s = await self._run_blocking(self.client.get_symbol_info, symbol)
        if not s: return None
        return SymbolInfo(
            name=s.name, description=s.description, exchange=self.exchange_name,
            currency_base=s.base_currency, currency_profit=s.profit_currency,
            volume_min=s.volume_min, volume_max=s.volume_max,
            volume_step=s.volume_step, trade_contract_size=s.contract_size
        )

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        tick = await self._run_blocking(self.client.get_tick, symbol)
        if not tick: return None
        return TickData(
            symbol=symbol, time=tick.time, bid=tick.bid, ask=tick.ask, 
            last=tick.last, volume=tick.volume
        )

    async def get_historical_klines(self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime) -> List[KlineData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        timeframe = self._map_timeframe_to_mt5(timeframe_str)
        rates = await self._run_blocking(self.client.get_rates, symbol, timeframe, start_dt, end_dt)
        if rates is None: return []
        return [KlineData(
            time=int(r.time), open=r.open, high=r.high, low=r.low, close=r.close, tick_volume=int(r.tick_volume)
        ) for r in rates]

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        order_type_mt5 = self._map_aura_order_type_to_mt5(order_request.type)
        
        try:
            result = await self._run_blocking(
                self.client.create_order,
                symbol=order_request.symbol,
                order_type=order_type_mt5,
                volume=order_request.volume,
                price=order_request.price,
                stop_loss=order_request.sl,
                take_profit=order_request.tp,
                magic=order_request.magic,
                comment=order_request.comment
            )
            if not result:
                raise ConnectionAbortedError("Order send failed, no result from terminal.")
            
            return OrderResult(
                retcode=result.retcode, deal=result.deal, order=result.order,
                volume=result.volume, price=result.price, bid=result.bid, ask=result.ask,
                comment=result.comment, request_id=result.request_id,
                retcode_message=result.comment
            )
        except Exception as e:
            raise ConnectionAbortedError(f"Order send failed via mt5-linux: {e}")

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        try:
            result = await self._run_blocking(self.client.cancel_order, int(order_id))
            if not result:
                raise ValueError("Cancel order failed, no result from terminal.")
            return {"status": "success", "message": result.comment, "details": result.to_dict()}
        except Exception as e:
            raise ValueError(f"Failed to cancel order {order_id}: {e}")

    async def get_open_positions(self) -> List[PositionInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        positions: List[Position] = await self._run_blocking(self.client.get_positions)
        if not positions: return []
        
        return [PositionInfo(
            ticket=p.ticket, symbol=p.symbol, type=p.type.name,
            volume=p.volume, price_open=p.price_open, price_current=p.price_current,
            sl=p.sl, tp=p.tp, profit=p.profit, time=p.time,
            magic=p.magic, comment=p.comment
        ) for p in positions]

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        deals: List[Deal] = await self._run_blocking(self.client.get_deals, start_date, end_date)
        if not deals: return []

        return [TradeHistoryInfo(
            ticket=d.ticket, order=d.order, symbol=d.symbol,
            type=d.type.name, entry=d.entry.name,
            volume=d.volume, price=d.price, profit=d.profit,
            time=d.time, magic=d.magic, comment=d.comment
        ) for d in deals]
        
    async def get_account_balance(self) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ValueError("MT5 is not connected.")
        
        info = await self._run_blocking(self.client.get_account_info)
        if not info: raise ValueError("Could not retrieve account info from MT5.")
        
        return {
            "name": info.name, "login": info.login, "server": info.server,
            "balance": info.balance, "equity": info.equity,
            "profit": info.profit, "currency": info.currency,
            "leverage": info.leverage, "margin": info.margin,
            "margin_free": info.margin_free, "margin_level": info.margin_level
        }
