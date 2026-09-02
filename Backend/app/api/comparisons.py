from fastapi import APIRouter, HTTPException

from app.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
)
from app.services.comparison_service import ComparisonService


router = APIRouter(
    prefix="/comparisons",
    tags=["Comparison Agent"],
)


@router.post(
    "/compare",
    response_model=ComparisonResponse,
)
async def compare_companies(
    request: ComparisonRequest,
):
    """
    Compare multiple companies based on the selected
    financial metrics and return rankings.
    """

    try:
        comparison_service = ComparisonService()

        result = comparison_service.compare(request)

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(error)}",
        )