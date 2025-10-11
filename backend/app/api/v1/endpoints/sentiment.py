"""
AuraQuant - API Endpoints for Sentiment Data
"""
import asyncio
import json
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from starlette.responses import StreamingResponse
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.kafka_producer import TOPIC_SENTIMENT_SCORES
from app.crud.sentiment import crud_sentiment
from app.schemas.sentiment import SentimentDataInDB

router = APIRouter()

@router.get("/historical/{symbol}", response_model=List[SentimentDataInDB])
async def get_historical_sentiment(
    symbol: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get historical sentiment scores for a symbol for the last 24 hours.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    return await crud_sentiment.get_by_symbol_and_daterange(db, symbol=symbol, start_date=start_date, end_date=end_date)


async def sentiment_event_stream(symbol: str):
    """
    The event generator for the Server-Sent Events (SSE) stream.
    """
    consumer = AIOKafkaConsumer(
        TOPIC_SENTIMENT_SCORES,
        bootstrap_servers='localhost:9092',
        group_id=f"sse_consumer_{symbol}_{datetime.now().timestamp()}", # Unique group_id per connection
        auto_offset_reset='latest' # Only get new messages
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            # Only yield the message if it matches the requested symbol
            if data.get("symbol") == symbol:
                # SSE format is "data: {json_string}\n\n"
                yield f"data: {json.dumps(data)}\n\n"
    finally:
        await consumer.stop()

@router.get("/stream/{symbol}")
async def stream_sentiment(
    symbol: str,
    request: Request, # FastAPI uses this to detect if the client has disconnected
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Subscribe to a real-time stream of sentiment scores for a specific symbol.
    """
    return StreamingResponse(sentiment_event_stream(symbol), media_type="text/event-stream")