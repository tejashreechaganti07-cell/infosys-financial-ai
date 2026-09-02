from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatQueryRequest(BaseModel):
    query: str
    workspace_id: str
    company_name: Optional[str] = None

class Citation(BaseModel):
    source: str
    page: Optional[str] = "1"
    quote: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: str
    workspace_id: str
    role: str  # "user" | "assistant"
    content: str
    reasoning_steps: Optional[List[str]] = None
    citations: Optional[List[Citation]] = None
    timestamp: str

class ChatQueryResponse(BaseModel):
    message: ChatMessageResponse
    agent_status: str = "Research Agent citation verified"

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
