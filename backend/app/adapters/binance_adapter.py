import asyncio
import httpx
import hmac
import logging
import hashlib
import time
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import websockets
from websockets.exceptions import ConnectionClosed

from app.core.config import settings
from app.core.exchange_adapter import ExchangeAdapterProtocol, ConnectionStatus
from app.schemas.market_data import SymbolInfo, TickData, KlineData
from app.schemas.trade import OrderRequest, OrderResult, PositionInfo, TradeHistoryInfo, OrderType

from app.kafka_producer import logger


class BinanceAdapter(ExchangeAdapterProtocol):
    exchange_name: str = "Binance"
    _status: ConnectionStatus = ConnectionStatus.DISCONNECTED

    def __init__(self):
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        # In a real system, you'd have separate URLs for testnet
        self.base_url = "https://api.binance.com"
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        self.http_client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        self.websocket_client = None
        self.websocket_listener_task = None
        self.stream_callbacks: Dict[str, callable] = {}  # Store callbacks for different streams
        self.depth_cache: Dict[str, Dict[str, Any]] = {}  # Cache for L2 order book data

    def _generate_signature(self, data_str: str) -> str:
        return hmac.new(self.api_secret.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()

    async def _private_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key or not self.api_secret:
            raise ConnectionError("Binance API key/secret not configured.")

        if params is None:
            params = {}

        params['timestamp'] = int(time.time() * 1000)
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = self._generate_signature(query_string)
        query_string += f"&signature={signature}"

        headers = {'X-MBX-APIKEY': self.api_key}
        url = f"{endpoint}?{query_string}"

        response = await self.http_client.request(method, url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def connect(self):
        self._status = ConnectionStatus.CONNECTING
        try:
            await self.http_client.get("/api/v3/ping")
            await self._private_request("GET", "/api/v3/account")
            self._status = ConnectionStatus.CONNECTED
            # Start the websocket listener in the background
            if not self.websocket_listener_task:
                 self.websocket_listener_task = asyncio.create_task(self._websocket_manager())
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            raise ConnectionError(f"Binance connection failed: {e}")

    async def disconnect(self):
        if self.websocket_listener_task:
            self.websocket_listener_task.cancel()
            self.websocket_listener_task = None
        if self.websocket_client and self.websocket_client.open:
            await self.websocket_client.close()
            self.websocket_client = None
        await self.http_client.aclose()
        self._status = ConnectionStatus.DISCONNECTED

    def get_status(self) -> ConnectionStatus:
        return self._status

    async def subscribe_to_streams(self, stream_names: List[str]):
        """Generic subscription method."""
        if not self.websocket_client or not self.websocket_client.open:
            raise ConnectionError("WebSocket is not connected.")

        subscribe_message = {"method": "SUBSCRIBE", "params": stream_names, "id": int(time.time())}
        await self.websocket_client.send(json.dumps(subscribe_message))
        self.subscribed_streams.update(stream_names)
        logger.info(f"Subscribed to Binance streams: {stream_names}")

    async def subscribe_to_order_book(self, symbol: str):
        """Subscribes to the L2 depth of book stream for a symbol."""
        stream_name = f"{symbol.lower()}@depth"
        # Set the callback for this specific stream
        self.stream_callbacks[stream_name] = self._handle_depth_update
        await self.subscribe_to_streams([stream_name])

    async def _websocket_manager(self):
        """A long-running task to manage the WebSocket connection and dispatch messages."""
        while True:
            try:
                async with websockets.connect(self.websocket_url) as ws:
                    self.websocket_client = ws
                    logger.info("Binance WebSocket connection established.")
                    # Re-subscribe to any active streams if we reconnected
                    if self.subscribed_streams:
                        await self.subscribe_to_streams(list(self.subscribed_streams))

                    async for message in ws:
                        data = json.loads(message)
                        stream_name = data.get('stream')
                        if stream_name and stream_name in self.stream_callbacks:
                            # --- DISPATCH TO APPROPRIATE HANDLER ---
                            await self.stream_callbacks[stream_name](data['data'])
            except (ConnectionClosed, asyncio.CancelledError):
                logger.warning("Binance WebSocket connection closed.")
                break
            except Exception as e:
                logger.error(f"Binance WebSocket error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
        self.websocket_client = None

    async def get_all_symbols(self) -> List[SymbolInfo]:
        response = await self.http_client.get("/api/v3/exchangeInfo")
        response.raise_for_status()
        data = response.json()

        symbol_list = []
        for s in data['symbols']:
            if s['status'] == 'TRADING' and 'SPOT' in s['permissions']:
                lot_size = next((f for f in s['filters'] if f['filterType'] == 'LOT_SIZE'), {})
                symbol_list.append(SymbolInfo(
                    name=s['symbol'], description=f"{s['baseAsset']}/{s['quoteAsset']}",
                    exchange=self.exchange_name, currency_base=s['baseAsset'], currency_profit=s['quoteAsset'],
                    volume_min=float(lot_size.get('minQty', 0.0)), volume_max=float(lot_size.get('maxQty', 0.0)),
                    volume_step=float(lot_size.get('stepSize', 0.0)), trade_contract_size=1.0
                ))
        return symbol_list

    async def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        # Binance API gets all symbols at once, so we filter from there.
        symbols = await self.get_all_symbols()
        return next((s for s in symbols if s.name == symbol), None)

    async def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        response = await self.http_client.get("/api/v3/ticker/24hr", params={"symbol": symbol})
        response.raise_for_status()
        tick = response.json()
        return TickData(
            symbol=symbol, time=datetime.fromtimestamp(tick['closeTime'] / 1000),
            bid=float(tick['bidPrice']), ask=float(tick['askPrice']),
            last=float(tick['lastPrice']), volume=int(float(tick['volume']))
        )

    async def get_historical_klines(
        self, symbol: str, timeframe_str: str, start_dt: datetime, end_dt: datetime
    ) -> List[KlineData]:
        # Binance uses a different timeframe format, e.g., '1m', '1h', '1d'
        tf_map = {"1M": "1m", "5M": "5m", "15M": "15m", "30M": "30m", "1H": "1h", "4H": "4h", "1D": "1d", "1W": "1w"}
        interval = tf_map.get(timeframe_str.upper())
        if not interval: raise ValueError(f"Unsupported timeframe for Binance: {timeframe_str}")

        params = {
            "symbol": symbol, "interval": interval,
            "startTime": int(start_dt.timestamp() * 1000),
            "endTime": int(end_dt.timestamp() * 1000),
            "limit": 1000
        }
        response = await self.http_client.get("/api/v3/klines", params=params)
        response.raise_for_status()
        data = response.json()
        return [KlineData(
            time=int(k[0] / 1000), open=float(k[1]), high=float(k[2]),
            low=float(k[3]), close=float(k[4]), tick_volume=int(float(k[5]))
        ) for k in data]

    async def place_order(self, order_request: OrderRequest) -> OrderResult:
        # NOTE: This is a simplified mapping. A full implementation would handle all order types.
        side = "BUY" if "BUY" in order_request.type.upper() else "SELL"
        order_type = "LIMIT" if "LIMIT" in order_request.type.upper() else "MARKET"

        params = {
            "symbol": order_request.symbol,
            "side": side,
            "type": order_type,
            "quantity": order_request.volume,
        }
        if order_type == "LIMIT":
            params["price"] = order_request.price
            params["timeInForce"] = "GTC" # Good Till Canceled

        result = await self._private_request("POST", "/api/v3/order", params=params)

        # Binance result is very different from MT5. We map it to our OrderResult schema.
        # This is a key part of the adapter's job.
        return OrderResult(
            retcode=0, # Use 0 for success from Binance
            deal=result.get('transactTime', 0), # Using transactTime as a deal identifier
            order=result['orderId'],
            volume=float(result['executedQty']),
            price=float(result.get('price', 0.0) or result.get('cummulativeQuoteQty', 0.0) / float(result['executedQty'])),
            bid=0.0, ask=0.0, # Not available in order response
            comment=f"Binance order {result['status']}",
            request_id=result.get('orderId', 0),
            retcode_message=result['status']
        )

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        params = {"symbol": symbol, "orderId": int(order_id)}
        result = await self._private_request("DELETE", "/api/v3/order", params=params)
        return {"status": "success", "message": "Order canceled", "details": result}

    async def get_open_positions(self) -> List[PositionInfo]:
        # For SPOT market, "positions" are just asset balances. This is a significant
        # difference from futures/CFD platforms like MT5.
        account_info = await self.get_account_balance()
        positions = []
        for asset in account_info['balances']:
            if float(asset['free']) > 0 or float(asset['locked']) > 0:
                positions.append(PositionInfo(
                    ticket=int(time.time()), # No ticket in Binance, generate one
                    symbol=f"{asset['asset']}BUSD", # Assuming BUSD as a common quote
                    type="BUY", # N/A for spot balances
                    volume=float(asset['free']) + float(asset['locked']),
                    price_open=0.0, price_current=0.0, # N/A for spot balances
                    sl=0.0, tp=0.0, profit=0.0, # N/A
                    time=datetime.now(timezone.utc), magic=0, comment="SPOT Balance"
                ))
        return positions

    async def get_trade_history(self, start_date: datetime, end_date: datetime) -> List[TradeHistoryInfo]:
        # This is a complex operation requiring fetching trades for all symbols.
        # For this example, we'll implement for a single symbol.
        # A full implementation would iterate over user's frequently traded symbols.
        symbol = "BTCUSDT" # Example symbol
        params = {
            "symbol": symbol,
            "startTime": int(start_date.timestamp() * 1000),
            "endTime": int(end_date.timestamp() * 1000),
        }
        trades = await self._private_request("GET", "/api/v3/myTrades", params=params)

        return [TradeHistoryInfo(
            ticket=t['id'], order=t['orderId'], symbol=t['symbol'],
            type="BUY" if t['isBuyer'] else "SELL",
            entry="IN" if t['isBuyer'] else "OUT", # Heuristic mapping
            volume=float(t['qty']), price=float(t['price']),
            profit=0.0, # Profit is not calculated per-trade in Binance spot
            time=datetime.fromtimestamp(t['time']/1000), magic=0, comment=f"Commission: {t['commission']}"
        ) for t in trades]

    async def get_account_balance(self) -> Dict[str, Any]:
        return await self._private_request("GET", "/api/v3/account")