from fastapi import APIRouter, Depends
from app.schemas.dashboard import StatsCardsResponse, DashboardSummaryResponse
from app.services.dashboard_service import DashboardService
from app.core.security import get_current_user_token

router = APIRouter(prefix="/dashboard", tags=["Dashboard KPIs"])

@router.get("", response_model=DashboardSummaryResponse)
@router.get("/", response_model=DashboardSummaryResponse)
@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await DashboardService.get_summary(user_id)

@router.get("/stats", response_model=StatsCardsResponse)
async def get_dashboard_stats(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await DashboardService.get_stats(user_id)
