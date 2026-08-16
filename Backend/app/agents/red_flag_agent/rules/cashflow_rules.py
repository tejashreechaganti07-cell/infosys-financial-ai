from typing import List, Dict
import uuid
from app.agents.red_flag_agent.schemas import RedFlag

def check_negative_cashflow(metrics_by_year: Dict[int, Dict[str, dict]], document_id: str, company_name: str) -> List[RedFlag]:
    flags = []
    
    # We will track consecutive negative years
    consecutive_negative_years = 0
    
    for year in sorted(metrics_by_year.keys()):
        ocf_metric = metrics_by_year[year].get("Operating Cash Flow")
        if not ocf_metric or ocf_metric.get("value") is None:
            # Break consecutive chain if missing data
            consecutive_negative_years = 0
            continue
            
        ocf_val = ocf_metric["value"]
        
        if ocf_val < 0:
            consecutive_negative_years += 1
            severity = "high" if consecutive_negative_years > 1 else "medium"
            
            flags.append(RedFlag(
                flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                company_name=company_name,
                flag_type="negative_operating_cashflow",
                category="cash_flow",
                severity=severity,
                title="Negative Operating Cash Flow",
                description=f"Operating Cash Flow is negative ({ocf_val}) for fiscal year {year}. Consecutive negative years: {consecutive_negative_years}.",
                evidence_data={str(year): ocf_val},
                detected_metrics=[ocf_metric["metric_id"]],
                source_chunk_ids=ocf_metric.get("source_chunk_ids", [])
            ))
        else:
            consecutive_negative_years = 0
            
    return flags
