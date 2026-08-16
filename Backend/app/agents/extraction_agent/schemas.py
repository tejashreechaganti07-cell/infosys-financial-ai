from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ExtractedMetricInput(BaseModel):
    """The raw structured output from the LLM."""
    metric_name: str = Field(description="Name of the financial metric.")
    value: Optional[float] = Field(description="The numeric value of the metric.", default=None)
    original_value: Optional[str] = Field(description="The exact text string from the document representing the value.", default=None)
    currency: Optional[str] = Field(description="Currency code (e.g. USD, EUR).", default=None)
    unit: Optional[str] = Field(description="Unit scale (e.g. absolute, percent, million, billion).", default=None)
    fiscal_year: Optional[int] = Field(description="The fiscal year for this metric.", default=None)
    source_chunk_ids: List[str] = Field(description="IDs of the chunks providing evidence for this metric.", default=[])
    source_pages: List[int] = Field(description="Page numbers providing evidence for this metric.", default=[])
    confidence_score: float = Field(description="LLM's confidence score between 0.0 and 1.0.", default=0.0)

class ValidatedMetric(BaseModel):
    """The metric after normalization and evidence validation, ready for DB."""
    metric_id: str
    document_id: str
    company_name: Optional[str] = None
    metric_name: str
    fiscal_year: Optional[int]
    value: Optional[float]
    original_value: Optional[str]
    currency: Optional[str]
    unit: str
    source_type: str = "extracted"
    source_chunk_ids: List[str]
    source_pages: List[int]
    confidence_score: float
    status: str
    created_at: str

class DerivedMetric(BaseModel):
    """A deterministic metric calculated from other ValidatedMetrics."""
    metric_id: str
    document_id: str
    company_name: Optional[str] = None
    metric_name: str
    fiscal_year: Optional[int]
    value: Optional[float]
    unit: str
    source_type: str = "derived"
    calculation: str
    input_metric_ids: List[str]
    status: str
    created_at: str
