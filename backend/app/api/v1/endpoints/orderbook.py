"""
AuraQuant - API Endpoint for L2 Order Book Data
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models.user import User
from app.core.redis_client import redis_client

router = APIRouter()


@router.get("/{symbol}")
async def get_order_book_snapshot(
        symbol: str,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieves the latest L2 order book snapshot for a symbol from the cache.
    """
    redis_key = f"orderbook:{symbol.upper()}"
    snapshot = await redis_client.client.get(redis_key)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order book data for symbol '{symbol}' is not currently available. Please ensure the stream is active."
        )

    return json.loads(snapshot)