"""
AuraQuant - Redis Client for Task Queuing (Production Ready)
"""
import redis.asyncio as redis
import logging
from typing import Optional
from uuid import UUID
from app.core.config import settings # Import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        # --- MODIFIED: Read connection details from settings ---
        self.host = settings.REDIS_HOST or 'localhost'
        self.port = settings.REDIS_PORT or 6379
        self.password = settings.REDIS_PASSWORD or None
        
        self.client = redis.Redis(
            host=self.host, 
            port=self.port, 
            password=self.password,
            db=0, # Default DB for general use
            decode_responses=True
        )
        self.ORDER_QUEUE_KEY = "auraquant:order_submission_queue"

    async def connect(self):
        """Initializes the connection to the Redis server."""
        try:
            await self.client.ping()
            logger.info(f"Successfully connected to Redis at {self.host}:{self.port}.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def disconnect(self):
        """Closes the connection to the Redis server."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis.")

    async def enqueue_order(self, order_id: UUID):
        """Adds a new order's UUID to the submission queue."""
        if not self.client:
            raise ConnectionError("Redis is not connected.")
        await self.client.rpush(self.ORDER_QUEUE_KEY, str(order_id))

    async def dequeue_order(self) -> Optional[UUID]:
        """Atomically removes and returns an order ID from the queue."""
        if not self.client:
            raise ConnectionError("Redis is not connected.")
        
        result = await self.client.blpop(self.ORDER_QUEUE_KEY, timeout=0)
        
        if result:
            return UUID(result[1])
        return None

redis_client = RedisClient()
