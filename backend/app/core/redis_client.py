"""
AuraQuant - Redis Client for Task Queuing
"""
import redis.asyncio as redis
import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.ORDER_QUEUE_KEY = "auraquant:order_submission_queue"

    async def connect(self):
        try:
            await self.client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis.")

    async def enqueue_order(self, order_id: UUID):
        """Adds a new order ID to the submission queue."""
        if not self.client:
            raise ConnectionError("Redis is not connected.")
        await self.client.rpush(self.ORDER_QUEUE_KEY, str(order_id))

    async def dequeue_order(self) -> Optional[UUID]:
        """Removes and returns an order ID from the queue, blocking until one is available."""
        if not self.client:
            raise ConnectionError("Redis is not connected.")
        # BLPOP is a blocking pop, with a timeout of 0 to wait indefinitely
        result = await self.client.blpop(self.ORDER_QUEUE_KEY, timeout=0)
        return UUID(result[1]) if result else None

redis_client = RedisClient()