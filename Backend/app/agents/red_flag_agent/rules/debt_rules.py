from typing import List, Dict, Optional
import uuid
from app.agents.red_flag_agent.schemas import RedFlag
from app.agents.red_flag_agent.config import THRESHOLDS

def check_debt_growth(metrics_by_year: Dict[int, Dict[str, dict]], document_id: str, company_name: str) -> List[RedFlag]:
    flags = []
    years = sorted(metrics_by_year.keys())
    
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        
        prev_debt_metric = metrics_by_year[prev_year].get("Total Debt")
        curr_debt_metric = metrics_by_year[curr_year].get("Total Debt")
        
        if not prev_debt_metric or not curr_debt_metric:
            continue
            
        prev_debt = prev_debt_metric["value"]
        curr_debt = curr_debt_metric["value"]
        
        if prev_debt and curr_debt and prev_debt != 0:
            growth_pct = ((curr_debt - prev_debt) / abs(prev_debt)) * 100
            
            if growth_pct >= THRESHOLDS["sudden_change_percentage"]:
                severity = "high"
            elif growth_pct >= THRESHOLDS["debt_growth_percentage"]:
                severity = "medium"
            else:
                continue
                
            flags.append(RedFlag(
                flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                company_name=company_name,
                flag_type="debt_growth",
                category="debt",
                severity=severity,
                title="Significant Debt Increase",
                description=f"Total debt increased by {growth_pct:.2f}% from {prev_year} to {curr_year}.",
                evidence_data={str(prev_year): prev_debt, str(curr_year): curr_debt},
                detected_metrics=[prev_debt_metric["metric_id"], curr_debt_metric["metric_id"]],
                source_chunk_ids=list(set(prev_debt_metric.get("source_chunk_ids", []) + curr_debt_metric.get("source_chunk_ids", [])))
            ))
            
    return flags

def check_leverage(metrics_by_year: Dict[int, Dict[str, dict]], document_id: str, company_name: str) -> List[RedFlag]:
    flags = []
    for year, metrics in metrics_by_year.items():
        de_metric = metrics.get("Debt-to-Equity")
        if not de_metric or not de_metric.get("value"):
            continue
            
        de_ratio = de_metric["value"]
        
        if de_ratio > THRESHOLDS["debt_to_equity_ratio"]:
            flags.append(RedFlag(
                flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                company_name=company_name,
                flag_type="high_leverage",
                category="leverage",
                severity="high" if de_ratio > (THRESHOLDS["debt_to_equity_ratio"] * 1.5) else "medium",
                title="High Debt-to-Equity Ratio",
                description=f"Debt-to-Equity ratio for {year} is {de_ratio:.2f}, indicating elevated leverage.",
                evidence_data={str(year): de_ratio},
                detected_metrics=[de_metric["metric_id"]],
                # Derived metrics don't have direct chunks, but we could trace back if needed. Empty for now.
                source_chunk_ids=[]
            ))
            
    return flags
