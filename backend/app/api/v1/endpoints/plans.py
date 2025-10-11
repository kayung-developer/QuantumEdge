"""
AuraQuant - API Endpoints for Subscription Plans
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.schemas.plan import Plan

router = APIRouter()

@router.get("/", response_model=List[Plan])
async def read_public_plans(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve all active and public subscription plans.
    This is a public endpoint for the pricing page.
    """
    plans = await crud.crud_plan.get_public_plans(db, skip=skip, limit=limit)
    return plans

# Example of a future admin-only endpoint
# @router.post("/", response_model=Plan, status_code=201)
# async def create_plan(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     plan_in: PlanCreate,
#     current_user: User = Depends(deps.get_current_active_superuser)
# ):
#     """
#     Create a new subscription plan (Admin only).
#     """
#     plan = await crud.crud_plan.create(db, obj_in=plan_in)
#     return plan