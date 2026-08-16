import uuid
from datetime import datetime
from typing import List, Dict, Optional
from .schemas import ValidatedMetric, DerivedMetric
import logging

logger = logging.getLogger(__name__)

class DeterministicCalculator:
    # Define rules for derived metrics
    # format: derived_name: (formula_string, [input1, input2], lambda func)
    DERIVED_RULES = {
        "Gross Margin": (
            "Gross Profit / Revenue * 100",
            ["Gross Profit", "Revenue"],
            lambda g, r: (g / r * 100) if r != 0 else None
        ),
        "Operating Margin": (
            "Operating Income / Revenue * 100",
            ["Operating Income", "Revenue"],
            lambda o, r: (o / r * 100) if r != 0 else None
        ),
        "Net Profit Margin": (
            "Net Income / Revenue * 100",
            ["Net Income", "Revenue"],
            lambda n, r: (n / r * 100) if r != 0 else None
        ),
        "Debt-to-Equity": (
            "Total Debt / Total Equity",
            ["Total Debt", "Total Equity"],
            lambda d, e: (d / e) if e != 0 else None
        )
    }

    @classmethod
    def calculate_derived_metrics(cls, document_id: str, company_name: Optional[str], validated_metrics: List[ValidatedMetric]) -> List[DerivedMetric]:
        derived_results = []
        
        # Group metrics by fiscal year to ensure we only calculate using same-year inputs
        metrics_by_year: Dict[int, Dict[str, ValidatedMetric]] = {}
        for m in validated_metrics:
            if m.fiscal_year and m.value is not None and m.status == "extracted":
                if m.fiscal_year not in metrics_by_year:
                    metrics_by_year[m.fiscal_year] = {}
                metrics_by_year[m.fiscal_year][m.metric_name] = m
                
        # Perform calculations for each year
        for year, metrics_dict in metrics_by_year.items():
            for derived_name, (calc_str, required_inputs, calc_func) in cls.DERIVED_RULES.items():
                
                # Check if we have all inputs
                has_all_inputs = all(req in metrics_dict for req in required_inputs)
                if not has_all_inputs:
                    continue
                    
                inputs = [metrics_dict[req].value for req in required_inputs]
                input_ids = [metrics_dict[req].metric_id for req in required_inputs]
                
                try:
                    result_value = calc_func(*inputs)
                    
                    if result_value is not None:
                        unit = "percent" if "Margin" in derived_name else "ratio"
                        
                        derived_metric = DerivedMetric(
                            metric_id=f"derived_{uuid.uuid4().hex[:8]}",
                            document_id=document_id,
                            company_name=company_name,
                            metric_name=derived_name,
                            fiscal_year=year,
                            value=result_value,
                            unit=unit,
                            source_type="derived",
                            calculation=calc_str,
                            input_metric_ids=input_ids,
                            status="calculated",
                            created_at=datetime.utcnow().isoformat()
                        )
                        derived_results.append(derived_metric)
                except Exception as e:
                    logger.warning(f"Failed to calculate {derived_name} for year {year}: {e}")
                    
        return derived_results
