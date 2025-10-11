"""
AuraQuant - API Endpoints for Adaptive Portfolio Management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.adaptive import (  # Assumes these are created
    AdaptivePortfolioCreate, AdaptivePortfolioUpdate, AdaptivePortfolioInDB
)
from app.crud.adaptive import crud_adaptive_portfolio

router = APIRouter()


@router.post("/", response_model=AdaptivePortfolioInDB, status_code=status.HTTP_201_CREATED)
async def create_adaptive_portfolio(
        *,
        db: AsyncSession = Depends(deps.get_db),
        portfolio_in: AdaptivePortfolioCreate,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Create a new adaptive portfolio configuration for the user.
    """
    # A user can only have one portfolio for now, for simplicity
    existing = await crud_adaptive_portfolio.get_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="An adaptive portfolio already exists for this user.")

    return await crud_adaptive_portfolio.create_with_user(db, obj_in=portfolio_in, user_id=current_user.id)


@router.get("/", response_model=List[AdaptivePortfolioInDB])
async def get_user_adaptive_portfolios(
        db: AsyncSession = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get the user's adaptive portfolio configurations.
    """
    return await crud_adaptive_portfolio.get_multi_by_user(db, user_id=current_user.id)


@router.put("/{portfolio_id}", response_model=AdaptivePortfolioInDB)
async def update_adaptive_portfolio(
        *,
        db: AsyncSession = Depends(deps.get_db),
        portfolio_id: int,
        portfolio_in: AdaptivePortfolioUpdate,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Update the regime-to-strategy mapping for a portfolio.
    """
    portfolio = await crud_adaptive_portfolio.get(db, id=portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found.")

    return await crud_adaptive_portfolio.update(db, db_obj=portfolio, obj_in=portfolio_in)


@router.post("/{portfolio_id}/activate", response_model=AdaptivePortfolioInDB)
async def activate_portfolio(
        *,
        db: AsyncSession = Depends(deps.get_db),
        portfolio_id: int,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Activate or deactivate live adaptive trading for a portfolio.
    """
    portfolio = await crud_adaptive_portfolio.get(db, id=portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found.")

    # Toggle the is_active state
    update_data = {"is_active": not portfolio.is_active}
    return await crud_adaptive_portfolio.update(db, db_obj=portfolio, obj_in=update_data)