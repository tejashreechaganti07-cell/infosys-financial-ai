from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FinancialMetricSchema(BaseModel):
    metric: str
    fy23: str
    fy24: str
    yoy_change: str
    status: str  # "Positive" | "Neutral" | "Negative"

class RedFlagSchema(BaseModel):
    severity: str  # "High" | "Medium" | "Low" | "Info"
    title: str
    description: str
    citation: str

class ComparisonItemSchema(BaseModel):
    company: str
    revenue: str
    ebit_margin: str
    roe: str
    fcf_conversion: str

class ReportSectionsSchema(BaseModel):
    executive_summary: str
    key_financials: List[FinancialMetricSchema]
    red_flags: List[RedFlagSchema]
    comparison: List[ComparisonItemSchema]
    outlook: str

class ReportCreate(BaseModel):
    title: str
    workspace_id: str
    company_name: Optional[str] = "Infosys Limited"

class ReportResponse(BaseModel):
    id: str
    title: str
    workspace_id: str
    user_id: str
    company_name: str
    summary: str
    status: str
    created_at: str
    sections: Optional[ReportSectionsSchema] = None

class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int
