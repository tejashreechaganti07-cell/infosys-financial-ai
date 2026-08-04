from pydantic import BaseModel
from typing import Optional, List

class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str
    user_id: str
    created_at: str
    updated_at: str
    documents_count: int = 0

class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    total: int
