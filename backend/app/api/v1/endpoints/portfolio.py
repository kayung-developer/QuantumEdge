"""
AuraQuant - API Endpoints for Portfolio Intelligence (Corrected Robust Version)
"""
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.crud.order import crud_order
from app.services.portfolio_service import portfolio_service
from app.services.forensics_service import forensics_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.portfolio import (
    AnalysisRequest, PortfolioAnalysisResponse, OptimizationResponse, TradeForensicsResponse
)

router = APIRouter()


@router.post("/analysis", response_model=PortfolioAnalysisResponse)
async def get_portfolio_analysis(
        *,
        db: AsyncSession = Depends(deps.get_db),
        request_body: AnalysisRequest,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Runs a full historical performance analysis on the user's trading portfolio
    for a given date range.
    """
    try:
        results = await portfolio_service.run_portfolio_analysis(
            db, user=current_user, start_date=request_body.start_date, end_date=request_body.end_date
        )
        if "error" in results:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results["error"])

        return PortfolioAnalysisResponse(**results)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # In production, you would log the full exception `e` for debugging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred during analysis.")


@router.post("/optimize", response_model=OptimizationResponse)
async def get_portfolio_optimization(
        *,
        db: AsyncSession = Depends(deps.get_db),
        request_body: AnalysisRequest,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Runs a Mean-Variance Optimization on the user's historical trade returns
    to find the allocation that would have maximized the Sharpe ratio.
    """
    try:
        results = await portfolio_service.run_mean_variance_optimization(
            db, user=current_user, start_date=request_body.start_date, end_date=request_body.end_date
        )
        if "error" in results:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results["error"])

        return OptimizationResponse(**results)

    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred during optimization.")


@router.get("/forensics/{order_id}", response_model=TradeForensicsResponse)
async def get_trade_forensics_report(
        *,
        db: AsyncSession = Depends(deps.get_db),
        order_id: UUID,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieves a detailed forensic report for a single filled trade, including
    market context at the time of execution.
    """
    try:
        # First, verify the user owns this order
        order = await crud_order.get(db, id=order_id)
        if not order or order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or you do not have permission to view it."
            )

        report = await forensics_service.get_trade_forensics(db, order_id=order_id)
        if "error" in report:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=report["error"])

        # Manually construct the final response model to ensure correctness.
        # jsonable_encoder is needed because the 'order' object is a SQLAlchemy model instance,
        # which needs to be converted to a dictionary for the Pydantic model.
        return TradeForensicsResponse(
            order=jsonable_encoder(report['order_details']),
            performance=report['performance'],
            market_context_at_entry=report['market_context_at_entry']
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during forensic analysis."
        )