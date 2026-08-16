from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RedFlag(BaseModel):
    """Core structured representation of a financial red flag."""
    flag_id: str
    document_id: str
    company_name: Optional[str] = None
    flag_type: str = Field(description="e.g. debt_growth, margin_compression, going_concern")
    category: str = Field(description="e.g. debt, leverage, profitability, qualitative")
    severity: str = Field(description="low, medium, high", default="medium")
    title: str = Field(description="Short readable summary")
    description: str = Field(description="Detailed explanation of the risk")
    evidence_data: Dict[str, Any] = Field(description="Underlying values/metrics that triggered the flag", default={})
    detected_metrics: List[str] = Field(description="IDs of extracted_metrics associated with this flag", default=[])
    source_chunk_ids: List[str] = Field(description="Chunk IDs providing evidence", default=[])
    confidence_score: float = Field(description="Confidence of the detection (1.0 for math rules)", default=1.0)
    status: str = Field(description="active, dismissed, reviewed", default="active")
    detected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class QualitativeFlagInput(BaseModel):
    """The raw structured output from the LLM qualitative analysis."""
    category: str = Field(description="Category of the risk (e.g. going_concern, auditor_qualifications)")
    title: str = Field(description="Short descriptive title of the finding")
    description: str = Field(description="Explanation grounded ONLY in the text, not assumptions")
    severity: str = Field(description="low, medium, high based on your assessment")
    source_chunk_ids: List[str] = Field(description="The exact chunk_ids that contain this evidence")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
