"""
AuraQuant - API Endpoints for AI/ML Services
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body

from app.api import deps
from app.services.cv_service import cv_service, ChartCVService
from app.services.ml_service import ml_service, MLModelService
from app.services.market_data_service import market_data_service, MarketDataService
from app.schemas.ai import ChartPatternDetection, ModelInfo
from app.models.user import User

router = APIRouter()


@router.get("/models", response_model=List[ModelInfo])
async def get_registered_models(
        ml_service_instance: MLModelService = Depends(lambda: ml_service),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a list of all registered machine learning models from the model registry.
    """
    if not ml_service_instance.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MLflow service is not configured or available."
        )
    return ml_service_instance.list_registered_models()


@router.get("/patterns/{symbol}", response_model=List[ChartPatternDetection])
async def detect_chart_patterns(
        symbol: str,
        timeframe: str = "1H",
        limit: int = 200,  # Number of candles to analyze
        cv_service_instance: ChartCVService = Depends(lambda: cv_service),
        market_service_instance: MarketDataService = Depends(lambda: market_data_service),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Analyzes historical data for a symbol to detect common chart patterns
    using a Computer Vision model.
    """
    if not market_service_instance.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data service is not available to fetch data for analysis."
        )

    # 1. Fetch the data needed for analysis
    try:
        klines = market_service_instance.get_historical_klines(symbol, timeframe, limit)
        if not klines:
            return []  # Return empty list if no data is available
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 2. Run the detection
    detections = cv_service_instance.detect_patterns(klines)

    return detections