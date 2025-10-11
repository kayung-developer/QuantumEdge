"""
AuraQuant - Kafka Producer Service
"""
import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = None
        self.bootstrap_servers = bootstrap_servers

    async def start(self):
        """Initializes and starts the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka Producer started successfully.")
        except Exception as e:
            logger.error(f"Failed to start Kafka Producer: {e}")
            self.producer = None

    async def stop(self):
        """Stops the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka Producer stopped.")

    async def send(self, topic: str, message: dict):
        """Sends a message to a specific Kafka topic."""
        if not self.producer:
            raise ConnectionError("Kafka Producer is not running.")

        try:
            await self.producer.send_and_wait(topic, message)
        except Exception as e:
            logger.error(f"Failed to send message to Kafka topic '{topic}': {e}")


# --- Topics Definition ---
TOPIC_RAW_NEWS = "raw_news_articles"
TOPIC_SENTIMENT_SCORES = "sentiment_analysis_results"

# --- Global Instance ---
kafka_producer = KafkaProducerService()