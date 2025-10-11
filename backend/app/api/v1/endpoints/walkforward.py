"""
AuraQuant - API Endpoints for Walk-Forward Optimization
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from celery.result import AsyncResult

from app.api import deps
from app.models.user import User
from app.schemas.walkforward import WalkForwardJobCreate, WalkForwardJobInDB
from app.celery_worker import run_walk_forward_optimization

router = APIRouter()


@router.post("/launch", response_model=WalkForwardJobInDB, status_code=202)
async def launch_walk_forward_job(
        config: WalkForwardJobCreate,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Launch a new, long-running Walk-Forward Optimization job.
    """
    # --- Premium Feature Check ---
    if not current_user.subscription or current_user.subscription.plan.name not in ["Ultimate", "Premium"]:
         raise HTTPException(status_code=403, detail="Walk-Forward Optimization requires a Premium or Ultimate plan.")

    task = run_walk_forward_optimization.delay(config.model_dump())

    return WalkForwardJobInDB(
        id=task.id,
        status="PENDING",
        user_id=current_user.id,
        config=config,
        created_at=datetime.utcnow()
    )


@router.get("/{job_id}/status", response_model=WalkForwardJobInDB)
async def get_walk_forward_job_status(
        job_id: str,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get the status and results of a Walk-Forward Optimization job.
    """
    task_result = AsyncResult(job_id)

    status = task_result.status
    results_data = None
    overall_performance = None

    if task_result.successful():
        status = "SUCCESS"
        results_data = task_result.result.get("results")
        # TODO: Aggregate overall performance
    elif task_result.failed():
        status = "FAILURE"

    # This part is a simulation as we don't have a DB model for the job itself yet,
    # we are building the response from the Celery task state.
    # A full implementation would store the result in the DB.

    return WalkForwardJobInDB(
        id=job_id,
        status=status,
        user_id=current_user.id,  # This is an assumption
        config=WalkForwardJobCreate(**task_result.kwargs.get('config_dict', {})),
        results=results_data,
        overall_performance=overall_performance,
        created_at=datetime.utcnow(),  # Placeholder
        completed_at=datetime.utcnow() if status in ["SUCCESS", "FAILURE"] else None,
    )