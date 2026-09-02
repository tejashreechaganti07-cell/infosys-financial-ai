from pydantic import BaseModel
from typing import Optional, List

class DocumentResponse(BaseModel):
    id: str
    title: str
    company_name: str
    filing_type: str
    fiscal_year: int
    workspace_id: str
    user_id: str
    file_path: str
    file_size: int
    status: str
    is_seed: bool = False
    chunks_count: int = 0
    uploaded_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
