"""
AuraQuant - L2 Order Book Aggregation and Caching Service
"""
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from collections import OrderedDict

from app.kafka_producer import TOPIC_L2_ORDER_BOOK
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class OrderBookService:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self._consumer_task: Optional[asyncio.Task] = None
        # In-memory cache of full order books for each symbol
        self._order_books: Dict[str, Dict[str, OrderedDict]] = {}
        # How often to push a full snapshot to Redis (in seconds)
        self.redis_snapshot_interval = 1.0

    def _update_book_side(self, book_side: OrderedDict, updates: List[List[str]]):
        """Updates a side of the order book (bids or asks)."""
        for price_str, qty_str in updates:
            price = float(price_str)
            qty = float(qty_str)
            if qty > 0:
                book_side[price] = qty
            elif price in book_side:
                del book_side[price]

    async def _process_message(self, raw_message: str):
        """Processes a raw L2 update from Kafka and updates the in-memory book."""
        try:
            data = json.loads(raw_message)
            symbol = data['symbol']

            if symbol not in self._order_books:
                self._order_books[symbol] = {
                    "bids": OrderedDict(),
                    "asks": OrderedDict(),
                    "last_update": 0
                }

            book = self._order_books[symbol]
            self._update_book_side(book['bids'], data['bids'])
            self._update_book_side(book['asks'], data['asks'])

            # Sort bids descending and asks ascending
            book['bids'] = OrderedDict(sorted(book['bids'].items(), key=lambda t: t[0], reverse=True))
            book['asks'] = OrderedDict(sorted(book['asks'].items(), key=lambda t: t[0]))

            book['last_update'] = data['timestamp_ms']
        except Exception as e:
            logger.error(f"Error processing L2 message: {e}")

    async def _snapshot_to_redis_worker(self):
        """Periodically sends the full order book snapshot to Redis."""
        while True:
            await asyncio.sleep(self.redis_snapshot_interval)
            for symbol, book in self._order_books.items():
                # Prepare data for Redis (limit depth to e.g., 50 levels)
                snapshot = {
                    "bids": list(book['bids'].items())[:50],
                    "asks": list(book['asks'].items())[:50],
                    "timestamp_ms": book['last_update']
                }
                redis_key = f"orderbook:{symbol}"
                await redis_client.client.set(redis_key, json.dumps(snapshot))

    async def run_consumer(self):
        """The main loop for the Kafka consumer."""
        logger.info("Order Book Service consumer is running...")

        # Start the Redis snapshot worker in the background
        asyncio.create_task(self._snapshot_to_redis_worker())

        consumer = AIOKafkaConsumer(
            TOPIC_L2_ORDER_BOOK,
            bootstrap_servers=self.bootstrap_servers,
            group_id="order_book_service_group",
            auto_offset_reset='latest'
        )
        await consumer.start()
        try:
            async for msg in consumer:
                await self._process_message(msg.value)
        finally:
            await consumer.stop()

    def start(self):
        if not self._consumer_task or self._consumer_task.done():
            self._consumer_task = asyncio.create_task(self.run_consumer())

    def stop(self):
        if self._consumer_task:
            self._consumer_task.cancel()


order_book_service = OrderBookService()