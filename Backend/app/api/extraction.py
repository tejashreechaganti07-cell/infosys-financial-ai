from fastapi import APIRouter, Depends, HTTPException

from app.services.extraction_service import ExtractionService
from app.core.security import get_current_user_token


router = APIRouter(
    prefix="/extraction",
    tags=["Financial Data Extraction"]
)


@router.post("/{document_id}")
async def extract_financial_data(
    document_id: str,
    token_data: dict = Depends(get_current_user_token)
):
    user_id = token_data.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    result = await ExtractionService.extract_document(
        user_id=user_id,
        document_id=document_id
    )

    return result