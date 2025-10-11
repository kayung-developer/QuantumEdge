"""
AuraQuant - API Endpoints for the Strategy Marketplace
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends

from app.api import deps
from app.models.user import User
from app.schemas.marketplace import MarketplaceStrategyInDB, MarketplaceStrategyCreate
from app.crud.marketplace import crud_marketplace_strategy
from app.services.marketplace_service import marketplace_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=List[MarketplaceStrategyInDB])
async def get_live_marketplace_strategies(db: AsyncSession = Depends(deps.get_db)):
    """
    Get all strategies that are approved and live on the marketplace.
    """
    return await crud_marketplace_strategy.get_all_approved(db)


@router.post("/publish", response_model=MarketplaceStrategyInDB)
async def publish_strategy_to_marketplace(
        strategy_in: MarketplaceStrategyCreate,
        db: AsyncSession = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Submit a user's custom strategy for review and publication.
    """
    # In a real system, you'd fetch the user's saved (private) strategy code
    # from another table instead of having them submit it directly here.
    return await marketplace_service.submit_strategy_for_review(
        db, author_id=current_user.id, strategy_in=strategy_in
    )


@router.post("/{strategy_id}/subscribe", response_model=MarketplaceSubscriptionInDB)
async def subscribe_to_strategy(
        strategy_id: UUID,
        db: AsyncSession = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Subscribe the current user to a marketplace strategy.
    """
    return await marketplace_service.subscribe_to_strategy(
        db, user_id=current_user.id, strategy_id=strategy_id
    )