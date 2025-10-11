"""
AuraQuant - Sentiment Storage Service
"""
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from datetime import datetime

from app.kafka_producer import TOPIC_SENTIMENT_SCORES
from app.db.session import AsyncSessionLocal
from app.crud.sentiment import crud_sentiment  # Assumes this is created
from app.schemas.sentiment import SentimentDataCreate  # Assumes this is created

logger = logging.getLogger(__name__)


class SentimentStorageService:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self._consumer_task: Optional[asyncio.Task] = None

    async def _process_message(self, raw_message: str):
        """Saves a single sentiment result to the database."""
        try:
            data = json.loads(raw_message)

            # Convert timestamp string to datetime object
            timestamp = datetime.fromisoformat(data['published_at'].replace('Z', '+00:00'))

            sentiment_in = SentimentDataCreate(
                timestamp=timestamp,
                symbol=data['symbol'],
                sentiment_score=data['sentiment_score'],
                sentiment_label=data['sentiment_label'],
                source=data['source'],
                headline=data['headline']
            )

            async with AsyncSessionLocal() as db:
                await crud_sentiment.create(db, obj_in=sentiment_in)

        except Exception as e:
            logger.error(f"Error storing sentiment data: {e}")

    async def run_consumer(self):
        """
        The main loop for the Kafka consumer. Listens for structured sentiment results.
        """
        logger.info("Sentiment Storage consumer is running...")
        consumer = AIOKafkaConsumer(
            TOPIC_SENTIMENT_SCORES,
            bootstrap_servers=self.bootstrap_servers,
            group_id="sentiment_storage_group",
            auto_offset_reset='earliest'
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
            self._consumer_task = None


sentiment_storage_service = SentimentStorageService()