from typing import List, Dict
import uuid
from app.agents.red_flag_agent.schemas import RedFlag
from app.agents.red_flag_agent.config import THRESHOLDS

def check_profitability_decline(metrics_by_year: Dict[int, Dict[str, dict]], document_id: str, company_name: str) -> List[RedFlag]:
    flags = []
    years = sorted(metrics_by_year.keys())
    
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        
        prev_metric = metrics_by_year[prev_year].get("Net Income")
        curr_metric = metrics_by_year[curr_year].get("Net Income")
        
        if not prev_metric or not curr_metric:
            continue
            
        prev_val = prev_metric["value"]
        curr_val = curr_metric["value"]
        
        if prev_val and curr_val and prev_val > 0:
            change_pct = ((curr_val - prev_val) / abs(prev_val)) * 100
            
            # Decrease of more than X%
            if change_pct <= -THRESHOLDS["sudden_change_percentage"]:
                severity = "high"
            elif change_pct <= -THRESHOLDS["profit_decline_percentage"]:
                severity = "medium"
            else:
                continue
                
            flags.append(RedFlag(
                flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                company_name=company_name,
                flag_type="profit_decline",
                category="profitability",
                severity=severity,
                title="Significant Net Income Decline",
                description=f"Net Income declined by {abs(change_pct):.2f}% from {prev_year} to {curr_year}.",
                evidence_data={str(prev_year): prev_val, str(curr_year): curr_val},
                detected_metrics=[prev_metric["metric_id"], curr_metric["metric_id"]],
                source_chunk_ids=list(set(prev_metric.get("source_chunk_ids", []) + curr_metric.get("source_chunk_ids", [])))
            ))
            
    return flags

def check_margin_compression(metrics_by_year: Dict[int, Dict[str, dict]], document_id: str, company_name: str) -> List[RedFlag]:
    flags = []
    years = sorted(metrics_by_year.keys())
    
    for margin_metric_name in ["Gross Margin", "Operating Margin", "Net Profit Margin"]:
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            
            prev_metric = metrics_by_year[prev_year].get(margin_metric_name)
            curr_metric = metrics_by_year[curr_year].get(margin_metric_name)
            
            if not prev_metric or not curr_metric:
                continue
                
            prev_val = prev_metric["value"]
            curr_val = curr_metric["value"]
            
            if prev_val and curr_val:
                point_change = curr_val - prev_val
                
                if point_change <= -THRESHOLDS["margin_compression_points"]:
                    flags.append(RedFlag(
                        flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                        document_id=document_id,
                        company_name=company_name,
                        flag_type="margin_compression",
                        category="profitability",
                        severity="high" if point_change <= -(THRESHOLDS["margin_compression_points"] * 2) else "medium",
                        title=f"{margin_metric_name} Compression",
                        description=f"{margin_metric_name} declined by {abs(point_change):.2f} percentage points from {prev_year} to {curr_year}.",
                        evidence_data={str(prev_year): prev_val, str(curr_year): curr_val},
                        detected_metrics=[prev_metric["metric_id"], curr_metric["metric_id"]],
                        source_chunk_ids=[]
                    ))
                    
    return flags
