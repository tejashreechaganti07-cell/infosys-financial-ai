from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query, BackgroundTasks
from typing import Optional
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService
from app.core.security import get_current_user_token

router = APIRouter(prefix="/documents", tags=["Financial Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    company_name: str = Form("Infosys Limited"),
    filing_type: str = Form("Annual Report"),
    fiscal_year: int = Form(2024),
    token_data: dict = Depends(get_current_user_token)
):
    user_id = token_data.get("sub")
    return await DocumentService.upload_document(
        user_id=user_id,
        workspace_id=workspace_id,
        file=file,
        company_name=company_name,
        filing_type=filing_type,
        fiscal_year=fiscal_year,
        background_tasks=background_tasks
    )

@router.get("", response_model=DocumentListResponse)
@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    workspace_id: Optional[str] = Query(None),
    token_data: dict = Depends(get_current_user_token)
):
    user_id = token_data.get("sub")
    return await DocumentService.list_documents(user_id, workspace_id)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await DocumentService.get_document(user_id, document_id)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    await DocumentService.delete_document(user_id, document_id)
    return None
