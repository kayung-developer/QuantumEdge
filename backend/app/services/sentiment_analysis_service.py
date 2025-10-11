"""
AuraQuant - Real-Time Sentiment Analysis Service
"""
import asyncio
import json
import logging
from typing import Optional

from aiokafka import AIOKafkaConsumer
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

from app.kafka_producer import kafka_producer, TOPIC_RAW_NEWS, TOPIC_SENTIMENT_SCORES

logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self._consumer_task: Optional[asyncio.Task] = None
        self.nlp_pipeline = None
        self.entity_map = {  # Simple mapping to link keywords to tradable symbols
            "Bitcoin": "BTCUSDT", "BTC": "BTCUSDT",
            "Ethereum": "ETHUSDT", "ETH": "ETHUSDT",
        }

    def _load_model(self):
        """
        Loads the pre-trained, finance-specific transformer model.
        This is a one-time, memory-intensive operation.
        """
        try:
            logger.info("Loading FinBERT sentiment analysis model...")
            # Using a model specifically fine-tuned on financial text
            model_name = "ProsusAI/finbert"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.nlp_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            logger.info("FinBERT model loaded successfully.")
        except Exception as e:
            logger.error(f"FATAL: Could not load NLP model. Sentiment Analysis will be disabled. Error: {e}")

    async def _process_message(self, raw_message: str):
        """Analyzes a single news article."""
        if not self.nlp_pipeline: return

        try:
            article = json.loads(raw_message)
            text_to_analyze = (article['title'] or '') + ". " + (article['description'] or '')
            if not text_to_analyze.strip(): return

            # Perform sentiment analysis
            results = self.nlp_pipeline(text_to_analyze)
            sentiment = results[0]  # The pipeline returns a list

            # Identify relevant entities (symbols)
            detected_symbols = set()
            for keyword, symbol in self.entity_map.items():
                if keyword.lower() in text_to_analyze.lower():
                    detected_symbols.add(symbol)

            if not detected_symbols: return

            # Publish a structured result for each detected symbol
            for symbol in detected_symbols:
                score = sentiment['score']
                # Convert label to a numerical score: positive=1, neutral=0, negative=-1
                if sentiment['label'] == 'negative':
                    score = -score
                elif sentiment['label'] == 'neutral':
                    score = 0

                sentiment_result = {
                    "symbol": symbol,
                    "sentiment_score": score,
                    "sentiment_label": sentiment['label'],
                    "source": article['source'],
                    "headline": article['title'],
                    "published_at": article['published_at']
                }
                await kafka_producer.send(TOPIC_SENTIMENT_SCORES, sentiment_result)

        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")

    async def run_consumer(self):
        """
        The main loop for the Kafka consumer. Listens for raw news articles.
        """
        self._load_model()
        if not self.nlp_pipeline: return

        logger.info("Sentiment Analysis consumer is running...")
        consumer = AIOKafkaConsumer(
            TOPIC_RAW_NEWS,
            bootstrap_servers=self.bootstrap_servers,
            group_id="sentiment_analyzer_group",
            auto_offset_reset='earliest'  # Start from the beginning if consumer is new
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


sentiment_analysis_service = SentimentAnalysisService()