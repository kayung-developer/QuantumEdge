"""
AuraQuant - MetaTrader 5 Exchange Adapter (Complete Cross-Platform Implementation)

This version uses the pure Python `MetaTraderPy` library to ensure compatibility
with Linux-based Docker environments and any non-Windows operating system. It fully
implements the ExchangeAdapterProtocol with native asyncio operations.
"""
import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any

from MetaTraderPy import MetaTraderPy
from MetaTraderPy.types import TimeFrame, OrderType as MT_OrderType, TradeAction, TradeResult, Position

from app.core.config import settings
from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo, OrderType as Aura_OrderType

class MT5Adapter(ExchangeAdapterProtocol):
    exchange_name: str = "MetaTrader5"
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    
    def __init__(self):
        login = int(settings.MT5_LOGIN) if settings.MT5_LOGIN else 0
        if not all([login, settings.MT5_PASSWORD, settings.MT5_SERVER]):
            # This adapter cannot function without credentials.
            self.client = None
            return
            
        self.client = MetaTraderPy(
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
            raise ConnectionError(f"MT5 connection failed using MetaTraderPy: {e}")

    async def disconnect(self):
        if self.client and self.get_status() == ConnectionStatus.CONNECTED:
            await self.client.disconnect()
        self._status = ConnectionStatus.DISCONNECTED

    def get_status(self) -> ConnectionStatus:
        if self.client and self.client.is_connected:
            self._status = ConnectionStatus.CONNECTED
        else:
            self._status = ConnectionStatus.DISCONNECTED
        return self._status

    def _map_timeframe(self, timeframe_str: str) -> TimeFrame:
        tf_map = {
            "1M": TimeFrame.TIME_FRAME_M1, "5M": TimeFrame.TIME_FRAME_M5, "15M": TimeFrame.TIME_FRAME_M15,
            "30M": TimeFrame.TIME_FRAME_M30, "1H": TimeFrame.TIME_FRAME_H1, "4H": TimeFrame.TIME_FRAME_H4,
            "1D": TimeFrame.TIME_FRAME_D1, "1W": TimeFrame.TIME_FRAME_W1, "1MN": TimeFrame.TIME_FRAME_MN1
        }
        timeframe = tf_map.get(timeframe_str.upper())
        if timeframe is None: raise ValueError(f"Unsupported timeframe for MT5: {timeframe_str}")
        return timeframe
        
    def _map_order_type_to_mtpy(self, order_type: Aura_OrderType) -> MT_OrderType:
        mapping = {
            Aura_OrderType.BUY: MT_OrderType.ORDER_TYPE_BUY,
            Aura_OrderType.SELL: MT_OrderType.ORDER_TYPE_SELL,
            Aura_OrderType.BUY_LIMIT: MT_OrderType.ORDER_TYPE_BUY_LIMIT,
            Aura_OrderType.SELL_LIMIT: MT_OrderType.ORDER_TYPE_SELL_LIMIT,
            Aura_OrderType.BUY_STOP: MT_OrderType.ORDER_TYPE_BUY_STOP,
            Aura_OrderType.SELL_STOP: MT_OrderType.ORDER_TYPE_SELL_STOP,
        }
        return mapping[order_type]

    async def get_all_symbols(self) -> List[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        symbol_names = await self.client.get_symbols()
        tasks = [self.get_symbol_info(s) for s in symbol_names]
        results = await asyncio.gather(*tasks)
        return [res for res in results if res is not None and "forex" in res.description.lower()] # Filter for forex symbols

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        info = await self.client.get_symbol_info(symbol)
        if not info: return None
        return SymbolInfo(
            name=info.get('name'), description=info.get('description'), exchange=self.exchange_name,
            currency_base=info.get('currencyBase'), currency_profit=info.get('currencyMargin'),
            volume_min=info.get('volumeMin'), volume_max=info.get('volumeMax'),
            volume_step=info.get('volumeStep'), trade_contract_size=info.get('tradeContractSize')
        )

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return None
        tick = await self.client.get_symbol_price(symbol)
        if not tick: return None
        return TickData(
            symbol=symbol, time=datetime.now(), # MetaTraderPy does not provide tick timestamp
            bid=tick.get('bid'), ask=tick.get('ask'), last=tick.get('last'), volume=0
        )

    async def get_historical_klines(self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime) -> List[KlineData]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        timeframe = self._map_timeframe(timeframe_str)
        rates = await self.client.get_historic_data(symbol, timeframe, start_dt, end_dt)
        if not rates: return []
        return [KlineData(
            time=int(r['time']), open=r['open'], high=r['high'],
            low=r['low'], close=r['close'], tick_volume=int(r['tickVolume'])
        ) for r in rates]

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        mt5_order_type = self._map_order_type_to_mtpy(order_request.type)
        
        # MetaTraderPy uses an explicit dictionary for trade requests
        request = {
            "symbol": order_request.symbol,
            "volume": order_request.volume,
            "type": mt5_order_type,
            "price": order_request.price,
            "stop_loss": order_request.sl,
            "take_profit": order_request.tp,
            "magic": order_request.magic,
            "comment": order_request.comment
        }
        
        try:
            result: TradeResult = await self.client.create_order(request)
            # Map the result back to our internal OrderResult schema
            return OrderResult(
                retcode=result.get('retcode'),
                deal=result.get('dealId', 0),
                order=result.get('orderId', 0),
                volume=result.get('volume', 0.0),
                price=result.get('price', 0.0),
                bid=result.get('bid', 0.0),
                ask=result.get('ask', 0.0),
                comment=result.get('comment', "No comment"),
                request_id=result.get('requestId', 0),
                retcode_message=result.get('comment', "No comment")
            )
        except Exception as e:
            raise ConnectionAbortedError(f"Order send failed via MetaTraderPy: {e}")

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ConnectionError("MT5 is not connected.")
        
        try:
            result = await self.client.cancel_order(int(order_id))
            return {"status": "success", "message": result.get('comment'), "details": result}
        except Exception as e:
            raise ValueError(f"Failed to cancel order {order_id}: {e}")

    def _map_position_type(self, pos_type: str) -> str:
        return "BUY" if pos_type == 'POSITION_TYPE_BUY' else "SELL"

    async def get_open_positions(self) -> List[PositionInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        
        positions: List[Position] = await self.client.get_positions()
        if not positions: return []
        
        return [PositionInfo(
            ticket=pos.get('ticket'), symbol=pos.get('symbol'), type=self._map_position_type(pos.get('type')),
            volume=pos.get('volume'), price_open=pos.get('priceOpen'), price_current=pos.get('priceCurrent'),
            sl=pos.get('stopLoss'), tp=pos.get('takeProfit'), profit=pos.get('profit'),
            time=datetime.fromtimestamp(pos.get('time')), magic=pos.get('magic'), comment=pos.get('comment')
        ) for pos in positions]

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        if self.get_status() != ConnectionStatus.CONNECTED: return []
        
        deals = await self.client.get_historic_deals(start_date, end_date)
        if not deals: return []

        return [TradeHistoryInfo(
            ticket=d.get('ticket'), order=d.get('order'), symbol=d.get('symbol'),
            type="BUY" if d.get('type') == 'DEAL_TYPE_BUY' else "SELL",
            entry="IN" if d.get('entry') == 'DEAL_ENTRY_IN' else "OUT",
            volume=d.get('volume'), price=d.get('price'), profit=d.get('profit'),
            time=datetime.fromtimestamp(d.get('time')), magic=d.get('magic'), comment=d.get('comment')
        ) for d in deals]
        
    async def get_account_balance(self) -> Dict[str, Any]:
        if self.get_status() != ConnectionStatus.CONNECTED: raise ValueError("MT5 is not connected.")
        
        info = await self.client.get_account_information()
        if not info: raise ValueError("Could not retrieve account info from MT5.")
        
        return {
            "balance": info.get('balance'), "equity": info.get('equity'),
            "profit": info.get('profit'), "currency": info.get('currency'),
            "leverage": info.get('leverage'), "margin": info.get('margin'),
            "margin_free": info.get('marginFree'), "margin_level": info.get('marginLevel')
        }
