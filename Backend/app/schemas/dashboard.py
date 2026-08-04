from pydantic import BaseModel
from typing import List, Dict, Any
from app.schemas.document import DocumentResponse
from app.schemas.workspace import WorkspaceResponse

class StatsCard(BaseModel):
    title: str
    value: str
    change: str
    trend: str  # "up" | "down" | "neutral"
    icon: str

class StatsCardsResponse(BaseModel):
    cards: List[StatsCard]

class DashboardSummaryResponse(BaseModel):
    stats: List[StatsCard]
    recent_documents: List[DocumentResponse]
    recent_workspaces: List[WorkspaceResponse]
    recent_reports: List[Dict[str, Any]]
