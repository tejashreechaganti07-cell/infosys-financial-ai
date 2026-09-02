from fastapi import APIRouter, Depends, status, Response
from app.schemas.report import ReportCreate, ReportResponse, ReportListResponse
from app.services.report_service import ReportService
from app.core.security import get_current_user_token

router = APIRouter(prefix="/reports", tags=["Analyst Reports"])

@router.get("", response_model=ReportListResponse)
@router.get("/", response_model=ReportListResponse)
async def list_reports(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await ReportService.list_reports(user_id)

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report_in: ReportCreate, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await ReportService.create_report(user_id, report_in)

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await ReportService.get_report(user_id, report_id)

@router.get("/{report_id}/export")
async def export_report(report_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    md_content = await ReportService.generate_markdown(user_id, report_id)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=analyst_report_{report_id}.md"}
    )
