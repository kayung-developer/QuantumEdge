"""
AuraQuant - News Ingestion Service
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from newsapi import NewsApiClient

from app.core.config import settings
from app.kafka_producer import kafka_producer, TOPIC_RAW_NEWS

logger = logging.getLogger(__name__)


class NewsIngestionService:
    def __init__(self):
        if not settings.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not configured. News Ingestion Service will be disabled.")
            self.api_client = None
        else:
            self.api_client = NewsApiClient(api_key=settings.NEWS_API_KEY)

        self._worker_task: Optional[asyncio.Task] = None
        # In production, you'd have a more sophisticated list of keywords
        self.keywords = ["Bitcoin", "Ethereum", "Forex", "Stock Market", "Federal Reserve", "ECB"]
        self.check_interval_seconds = 3600  # Fetch news every hour

    async def _fetch_and_publish(self):
        """Fetches latest news and publishes each article to Kafka."""
        if not self.api_client:
            return

        logger.info(f"Fetching news for keywords: {self.keywords}")
        try:
            # Fetch news from the last hour
            from_date = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')

            response = self.api_client.get_everything(
                q=' OR '.join(self.keywords),
                language='en',
                sort_by='publishedAt',
                from_param=from_date
            )

            if response['status'] == 'ok':
                articles = response['articles']
                logger.info(f"Fetched {len(articles)} new articles.")
                for article in articles:
                    # Construct a clean message
                    message = {
                        "source": article['source']['name'],
                        "author": article['author'],
                        "title": article['title'],
                        "description": article['description'],
                        "url": article['url'],
                        "published_at": article['publishedAt'],
                        "content": article.get('content', '')
                    }
                    # Send to Kafka for downstream processing
                    await kafka_producer.send(TOPIC_RAW_NEWS, message)
            else:
                logger.error(f"Error from NewsAPI: {response.get('message')}")

        except Exception as e:
            logger.error(f"An error occurred during news fetching: {e}")

    async def run_worker(self):
        """The main loop for the background worker."""
        logger.info("News Ingestion Service worker is running...")
        while True:
            await self._fetch_and_publish()
            await asyncio.sleep(self.check_interval_seconds)

    def start(self):
        if not self.api_client: return
        if not self._worker_task or self._worker_task.done():
            self._worker_task = asyncio.create_task(self.run_worker())

    def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None


news_ingestion_service = NewsIngestionService()