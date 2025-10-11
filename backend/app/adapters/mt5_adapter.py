"""
AuraQuant - MetaTrader 5 Exchange Adapter (Definitive Complete Cross-Platform Implementation)

This version uses the pure Python `pymt5adapter` library, which is available on PyPI
and provides a reliable, asynchronous interface to the MetaTrader 5 terminal,
ensuring compatibility with Linux-based Docker environments. All methods from the
ExchangeAdapterProtocol are fully implemented.
"""
import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any

from pymt5adapter import MT5Adapter as PyMT5Adapter, TimeFrame
from pymt5adapter.const import (
    ORDER_TYPE_BUY, ORDER_TYPE_SELL, ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT,
    ORDER_TYPE_BUY_STOP, ORDER_TYPE_SELL_STOP, TRADE_ACTION_DEAL, TRADE_ACTION_PENDING,
    TRADE_ACTION_REMOVE, DEAL_ENTRY_IN, DEAL_TYPE_BUY, POSITION_TYPE_BUY
)

from app.core.config import settings
from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo, OrderType as AuraOrderType

class MT5Adapter(ExchangeAdapterProtocol):
    exchange_name: str = "MetaTrader5"
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    
    def __init__(self):
        login = int(settings.MT5_LOGIN) if settings.MT5_LOGIN else 0
        if not all([login, settings.MT5_PASSWORD, settings.MT5_SERVER]):
            self.client = None
            return
            
        self.client = PyMT5Adapter(
            login=login,
            password=settings.MT5_PASSWORD,
            server=settings.MT5_SERVER
        )

    async def connect(self):
        if not self.client:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError("MT5 credentials are not configured, cannot connect.")
            
        self._status = ConnectionStatus.CONNECTING
        try:
            await self.client.connect()
            self._status = ConnectionStatus.CONNECTED
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError(f"MT5 connection failed using pymt5adapter: {e}")

    async def disconnect(self):
        if self.client and self.get_status() == ConnectionStatus.CONNECTED:
            await self.client.disconnect()
        self._status = ConnectionStatus.DISCONNECTED

    def get_status(self) -> ConnectionStatus:
        return self._status

    def _map_timeframe(self, timeframe_str: str) -> TimeFrame:
        try:
            return TimeFrame[timeframe_str.upper()]
        except KeyError:
            raise ValueError(f"Unsupported timeframe for MT5: {timeframe_str}")
        
    def _map_order_type_to_mt5(self, order_type: AuraOrderType) -> int:
        mapping = {
            AuraOrderType.BUY: ORDER_TYPE_BUY, AuraOrderType.SELL: ORDER_TYPE_SELL,
            AuraOrderType.BUY_LIMIT: ORDER_TYPE_BUY_LIMIT, AuraOrderType.SELL_LIMIT: ORDER_TYPE_SELL_LIMIT,
            AuraOrderType.BUY_STOP: ORDER_TYPE_BUY_STOP, AuraOrderType.SELL_STOP: ORDER_TYPE_SELL_STOP,
        }
        return mapping[order_type]

    def _map_mt5_pos_type_to_str(self, mt5_type: int) -> str:
        return "BUY" if mt5_type == POSITION_TYPE_BUY else "SELL"

    async def get_all_symbols(self) -> List[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        symbols_raw = await self.client.symbols_get()
        return [
            SymbolInfo(
                name=s['name'], description=s['description'], exchange=self.exchange_name,
                currency_base=s['currency_base'], currency_profit=s['currency_profit'],
                volume_min=s['volume_min'], volume_max=s['volume_max'],
                volume_step=s['volume_step'], trade_contract_size=s['trade_contract_size']
            ) for s in symbols_raw
        ]

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        info = await self.client.symbol_info(symbol)
        if not info: return None
        return SymbolInfo(
            name=info['name'], description=info['description'], exchange=self.exchange_name,
            currency_base=info['currency_base'], currency_profit=info['currency_profit'],
            volume_min=info['volume_min'], volume_max=info['volume_max'],
            volume_step=info['volume_step'], trade_contract_size=info['trade_contract_size']
        )

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        tick = await self.client.symbol_info_tick(symbol)
        if not tick: return None
        return TickData(
            symbol=symbol, time=datetime.fromtimestamp(tick['time_msc'] / 1000.0),
            bid=tick['bid'], ask=tick['ask'], last=tick['last'], volume=tick['volume']
        )

    async def get_historical_klines(self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime) -> List[KlineData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        timeframe = self._map_timeframe(timeframe_str)
        rates = await self.client.copy_rates_range(symbol, timeframe, start_dt, end_dt)
        if rates is None: return []
        return [KlineData(time=r[0], open=r[1], high=r[2], low=r[3], close=r[4], tick_volume=r[5]) for r in rates]

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        order_type_int = self._map_order_type_to_mt5(order_request.type)
        is_market_order = order_request.type in [AuraOrderType.BUY, AuraOrderType.SELL]
        
        request_dict = {
            "action": TRADE_ACTION_DEAL if is_market_order else TRADE_ACTION_PENDING,
            "symbol": order_request.symbol,
            "volume": order_request.volume,
            "type": order_type_int,
            "price": order_request.price if not is_market_order else 0.0,
            "sl": order_request.sl or 0.0,
            "tp": order_request.tp or 0.0,
            "magic": order_request.magic,
            "comment": order_request.comment,
            "deviation": order_request.deviation,
        }
        
        try:
            result = await self.client.order_send(request_dict)
            if not result:
                raise ConnectionAbortedError("Order send failed, no result from terminal.")
                
            return OrderResult(
                retcode=result['retcode'], deal=result['deal'], order=result['order'],
                volume=result['volume'], price=result['price'], bid=result['bid'], ask=result['ask'],
                comment=result['comment'], request_id=result['request'],
                retcode_message=result['comment']
            )
        except Exception as e:
            raise ConnectionAbortedError(f"Order send failed via pymt5adapter: {e}")

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        request_dict = {
            "action": TRADE_ACTION_REMOVE,
            "order": int(order_id),
        }
        try:
            result = await self.client.order_send(request_dict)
            if not result:
                raise ValueError("Cancel order failed, no result from terminal.")
            return {"status": "success", "message": result.get('comment'), "details": result}
        except Exception as e:
            raise ValueError(f"Failed to cancel order {order_id}: {e}")

    async def get_open_positions(self) -> List[PositionInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        positions = await self.client.positions_get()
        if not positions: return []
        
        return [PositionInfo(
            ticket=p['ticket'], symbol=p['symbol'], type=self._map_mt5_pos_type_to_str(p['type']),
            volume=p['volume'], price_open=p['price_open'], price_current=p['price_current'],
            sl=p['sl'], tp=p['tp'], profit=p['profit'], time=datetime.fromtimestamp(p['time']),
            magic=p['magic'], comment=p['comment']
        ) for p in positions]

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        deals = await self.client.history_deals_get(start_date, end_date)
        if not deals: return []

        return [TradeHistoryInfo(
            ticket=d['ticket'], order=d['order'], symbol=d['symbol'],
            type="BUY" if d['type'] == DEAL_TYPE_BUY else "SELL",
            entry="IN" if d['entry'] == DEAL_ENTRY_IN else "OUT",
            volume=d['volume'], price=d['price'], profit=d['profit'],
            time=datetime.fromtimestamp(d['time']), magic=d['magic'], comment=d['comment']
        ) for d in deals]
        
    async def get_account_balance(self) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ValueError("MT5 is not connected.")
        
        info = await self.client.account_info()
        if not info: raise ValueError("Could not retrieve account info from MT5.")
        
        return {
            "balance": info.get('balance'), "equity": info.get('equity'),
            "profit": info.get('profit'), "currency": info.get('currency'),
            "leverage": info.get('leverage'), "margin": info.get('margin'),
            "margin_free": info.get('margin_free'), "margin_level": info.get('margin_level')
        }
