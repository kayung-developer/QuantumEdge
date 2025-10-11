"""
AuraQuant - API Endpoints for AutoML Strategy Forging
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.forge import ForgeJobCreate, ForgeJobInDB  # Assumes these are created
from app.services.forge_service import forge_service
from app.crud.forge import crud_forge_job

router = APIRouter()


@router.post("/launch", response_model=ForgeJobInDB, status_code=202)
async def launch_new_forge_job(
        *,
        db: AsyncSession = Depends(deps.get_db),
        config: ForgeJobCreate,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Launch a new AutoML Strategy Forging job.
    This is a premium, subscription-only feature.
    """
    # --- SUBSCRIPTION CHECK ---
    # In a real system, you would check the user's subscription here.
    if not current_user.subscription or current_user.subscription.plan.name != "Ultimate":
         raise HTTPException(status_code=403, detail="This feature requires an Ultimate subscription.")

    job = await forge_service.launch_forge_job(db, user_id=current_user.id, config=config.model_dump())
    return job


@router.get("/{job_id}", response_model=ForgeJobInDB)
async def get_forge_job_status(
        *,
        db: AsyncSession = Depends(deps.get_db),
        job_id: UUID,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get the status and results of a specific Forge job.
    """
    job = await crud_forge_job.get(db, id=job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job