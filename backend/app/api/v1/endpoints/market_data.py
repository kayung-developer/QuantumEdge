"""
AuraQuant - API Endpoints for Market Data
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.schemas.market_data import SymbolInfo, KlineData, MarketStatus, TickData
from app.services.market_service import unified_market_service, UnifiedMarketService

from app.models.user import User

router = APIRouter()


# Dependency to check if the market data service is ready
def get_ready_market_service():
    if not market_data_service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data service is not available. Check connection to trading terminal."
        )
    return market_data_service


@router.get("/status", response_model=MarketStatus)
async def get_market_connection_status(
        service: UnifiedMarketService = Depends(lambda: unified_market_service),
        # current_user: User = Depends(deps.get_current_active_user), # Uncomment to protect
):
    """
    Get the current status of the connection to the trading terminal.
    """
    status = service.get_market_status()
    if not status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve market status."
        )
    return status


@router.get("/symbols", response_model=List[SymbolInfo])
async def get_available_symbols(
        service: UnifiedMarketService = Depends(lambda: unified_market_service),
        # current_user: User = Depends(deps.get_current_active_user), # Uncomment to protect
):
    """
    Retrieve a list of all available tradable symbols.
    """
    return service.get_all_symbols()


@router.get("/klines/{symbol}", response_model=List[KlineData])
async def get_klines(
        symbol: str,
        timeframe: str = "1H",
        limit: int = 500,
        service: UnifiedMarketService = Depends(lambda: unified_market_service),
        current_user: User = Depends(deps.get_current_active_user), # Uncomment to protect
):
    """
    Get historical candlestick (OHLCV) data for a specific symbol.
    """
    try:
        # Dates can be passed as query params
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=30)  # Example range
        data = await service.get_historical_klines(exchange_name, symbol, timeframe, start_dt, end_dt)
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/tick/{symbol}", response_model=TickData)
async def get_tick(
        symbol: str,
        service: UnifiedMarketService = Depends(lambda: unified_market_service),
        # current_user: User = Depends(deps.get_current_active_user), # Uncomment to protect
):
    """
    Get the latest real-time price tick for a specific symbol.
    """
    tick = service.get_latest_tick(symbol)
    if not tick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not retrieve tick data for symbol '{symbol}'."
        )
    return tick