from pydantic import BaseModel, Field
from typing import List, Optional, Any

class DocumentInput(BaseModel):
    document_id: str
    session_id: str
    user_id: str
    company_name: Optional[str] = None
    file_name: str
    file_path: Optional[str] = None
    mime_type: str = "application/pdf"

class DocumentMetadata(BaseModel):
    document_id: str
    page_count: int = 0
    document_type: str = "text_pdf"
    requires_ocr: bool = False
    processing_status: str = "uploaded"

class DocumentPage(BaseModel):
    document_id: str
    page_number: int
    text: str
    ocr_used: bool = False

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    page_start: int
    page_end: int
    section_type: str = "unknown"
    text: str
    token_count: int = 0

class DocumentTable(BaseModel):
    table_id: str
    document_id: str
    page_number: int
    title: Optional[str] = None
    headers: List[str] = []
    rows: List[dict] = []

class DocumentProcessingResult(BaseModel):
    document_id: str
    status: str
    page_count: int = 0
    chunks_created: int = 0
    tables_detected: int = 0
    embeddings_created: int = 0
