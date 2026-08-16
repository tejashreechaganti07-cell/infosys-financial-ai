import logging
from typing import List, Dict
from app.agents.red_flag_agent.schemas import RedFlag
from .debt_rules import check_debt_growth, check_leverage
from .profitability_rules import check_profitability_decline, check_margin_compression
from .cashflow_rules import check_negative_cashflow

logger = logging.getLogger(__name__)

class QuantitativeRuleEngine:
    @staticmethod
    def run_all_rules(metrics: List[dict], document_id: str, company_name: str) -> List[RedFlag]:
        """
        Executes all deterministic rules against the extracted and derived metrics.
        metrics: list of dicts (loaded from MongoDB).
        """
        # Group by year for easier analysis
        metrics_by_year: Dict[int, Dict[str, dict]] = {}
        for m in metrics:
            year = m.get("fiscal_year")
            if year is None:
                continue
                
            if year not in metrics_by_year:
                metrics_by_year[year] = {}
                
            metrics_by_year[year][m["metric_name"]] = m

        flags: List[RedFlag] = []
        
        try:
            flags.extend(check_debt_growth(metrics_by_year, document_id, company_name))
            flags.extend(check_leverage(metrics_by_year, document_id, company_name))
            flags.extend(check_profitability_decline(metrics_by_year, document_id, company_name))
            flags.extend(check_margin_compression(metrics_by_year, document_id, company_name))
            flags.extend(check_negative_cashflow(metrics_by_year, document_id, company_name))
            
            logger.info(f"Rule engine generated {len(flags)} quantitative flags.")
        except Exception as e:
            logger.error(f"Rule engine encountered an error: {e}")
            
        return flags
