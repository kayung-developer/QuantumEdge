"""
AuraQuant - API Endpoints for Trade Execution (Definitive Final Version)

This module provides the API endpoints for all trade-related actions.
- The POST /order endpoint interacts with the OrderOrchestratorService to accept
  new trade requests (both live and paper) in a fast, non-blocking way.
- The GET /order/{order_id} endpoint allows the frontend to poll for the
  real-time status of an order as it moves through the orchestration lifecycle.
- The GET /positions/{exchange_name} and /history/{exchange_name} endpoints
  interact with the UnifiedMarketService to fetch account-specific information
  directly from the target exchange.
"""
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.crud.order import crud_order
from app.schemas.order import OrderCreate, Order
# --- IMPORTS FOR RESPONSES ---
from app.schemas.trade import PositionInfo, TradeHistoryInfo

# --- SERVICE IMPORTS ---
from app.services.order_orchestrator import orchestrator_service, OrderOrchestratorService
from app.services.market_service import unified_market_service, UnifiedMarketService

router = APIRouter()

@router.post("/order", response_model=Order, status_code=status.HTTP_202_ACCEPTED)
async def create_new_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_active_user),
    orchestrator: OrderOrchestratorService = Depends(lambda: orchestrator_service),
):
    """
    Accepts a new trade order (live or paper), validates it against risk rules,
    persists it, and enqueues it for asynchronous execution.
    Returns immediately with the order's initial 'PENDING_SUBMIT' state.
    """
    try:
        db_order = await orchestrator.create_order(db, user=current_user, order_in=order_in)
        return db_order
    except (ValueError, ConnectionError, PermissionError) as e:
        # Catch specific, expected errors from services (e.g., risk violations, bad symbol)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the full error for debugging in a real production environment
        # logger.error(f"Unexpected error creating order for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while creating the order.")

@router.get("/order/{order_id}", response_model=Order)
async def get_order_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieves the current status of a specific orchestrated order from our internal database.
    This is used for polling by the frontend.
    """
    order = await crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order.")
    return order

@router.get("/positions/{exchange_name}", response_model=List[PositionInfo])
async def get_positions(
    exchange_name: str,
    service: UnifiedMarketService = Depends(lambda: unified_market_service),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieve all open trading positions directly from a specific exchange account.
    """
    try:
        return await service.get_open_positions(exchange_name)
    except ValueError as e:
        # This error is raised by the service if the exchange is not connected/found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching positions.")

@router.get("/history/{exchange_name}", response_model=List[TradeHistoryInfo])
async def get_history(
    exchange_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: UnifiedMarketService = Depends(lambda: unified_market_service),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieve trade history (fills/deals) for a specific exchange account.
    Defaults to the last 30 days if no date range is provided.
    """
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    try:
        return await service.get_trade_history(exchange_name, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching trade history.")