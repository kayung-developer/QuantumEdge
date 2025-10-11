"""
AuraQuant - API Endpoint for the Dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.services.dashboard_service import dashboard_service, DashboardService
from app.schemas.dashboard import DashboardSummary
from app.models.user import User

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    service: DashboardService = Depends(lambda: dashboard_service),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieve an aggregated summary of all data needed for the main dashboard.
    """
    summary = service.get_dashboard_summary()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate dashboard summary. Market or trade service may be unavailable."
        )
    return summary