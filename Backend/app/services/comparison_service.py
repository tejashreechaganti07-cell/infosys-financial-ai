from typing import Dict, List, Optional

from app.schemas.comparison import (
    CompanyMetrics,
    CompanyRanking,
    ComparisonRequest,
    ComparisonResponse,
    MetricComparison,
)


class ComparisonService:
    """
    Service responsible for comparing multiple companies,
    calculating normalized scores, and generating rankings.
    """

    # Metrics where a higher value is considered better
    HIGHER_IS_BETTER = {
        "revenue",
        "revenue_growth",
        "net_income",
        "profit",
        "profit_margin",
        "ebit_margin",
        "operating_margin",
        "free_cash_flow",
        "current_ratio",
        "roe",
        "roa",
    }

    # Metrics where a lower value is considered better
    LOWER_IS_BETTER = {
        "debt",
        "total_debt",
        "debt_to_equity",
        "debt_to_assets",
    }

    def get_criteria(
        self,
        companies: List[CompanyMetrics],
        criteria: Optional[List[str]],
    ) -> List[str]:
        """
        Use provided criteria. If no criteria is provided,
        automatically find common metrics.
        """

        if criteria:
            return criteria

        if not companies:
            return []

        common_metrics = set(companies[0].metrics.keys())

        for company in companies[1:]:
            common_metrics &= set(company.metrics.keys())

        return sorted(common_metrics)

    def is_higher_better(self, metric: str) -> bool:
        """
        Determines whether a higher value is better for a metric.
        Unknown metrics default to higher-is-better.
        """

        metric = metric.lower()

        if metric in self.LOWER_IS_BETTER:
            return False

        return True

    def calculate_metric_scores(
        self,
        companies: List[CompanyMetrics],
        metric: str,
    ) -> Dict[str, float]:
        """
        Normalize a metric into a score between 0 and 100.
        """

        valid_values = []

        for company in companies:
            value = company.metrics.get(metric)

            if value is not None:
                valid_values.append(float(value))

        if not valid_values:
            return {
                company.company_name: 0.0
                for company in companies
            }

        min_value = min(valid_values)
        max_value = max(valid_values)

        scores = {}

        # If every company has the same value,
        # give everyone the same full score.
        if min_value == max_value:
            for company in companies:
                if company.metrics.get(metric) is not None:
                    scores[company.company_name] = 100.0
                else:
                    scores[company.company_name] = 0.0

            return scores

        higher_is_better = self.is_higher_better(metric)

        for company in companies:
            value = company.metrics.get(metric)

            if value is None:
                scores[company.company_name] = 0.0
                continue

            value = float(value)

            if higher_is_better:
                score = (
                    (value - min_value)
                    / (max_value - min_value)
                    * 100
                )
            else:
                score = (
                    (max_value - value)
                    / (max_value - min_value)
                    * 100
                )

            scores[company.company_name] = round(score, 2)

        return scores

    def compare_metric(
        self,
        companies: List[CompanyMetrics],
        metric: str,
    ) -> MetricComparison:
        """
        Compare a single metric and determine the leader.
        """

        values = {
            company.company_name: company.metrics.get(metric)
            for company in companies
        }

        valid_values = {
            name: value
            for name, value in values.items()
            if value is not None
        }

        higher_is_better = self.is_higher_better(metric)

        leader = None

        if valid_values:
            if higher_is_better:
                leader = max(
                    valid_values,
                    key=valid_values.get
                )
            else:
                leader = min(
                    valid_values,
                    key=valid_values.get
                )

        return MetricComparison(
            metric=metric,
            values=values,
            leader=leader,
            higher_is_better=higher_is_better,
        )

    def compare(
        self,
        request: ComparisonRequest,
    ) -> ComparisonResponse:
        """
        Main Comparison Agent workflow.
        """

        companies = request.companies

        criteria = self.get_criteria(
            companies,
            request.criteria,
        )

        metric_comparisons = []
        all_metric_scores = {}

        # Compare every metric
        for metric in criteria:
            comparison = self.compare_metric(
                companies,
                metric,
            )

            metric_comparisons.append(comparison)

            all_metric_scores[metric] = (
                self.calculate_metric_scores(
                    companies,
                    metric,
                )
            )

        rankings = []

        # Calculate weighted overall score
        for company in companies:
            weighted_score = 0.0
            total_weight = 0.0

            metric_scores = {}

            for metric in criteria:
                score = all_metric_scores[metric].get(
                    company.company_name,
                    0.0,
                )

                weight = 1.0

                if request.weights:
                    weight = request.weights.get(
                        metric,
                        1.0,
                    )

                metric_scores[metric] = score

                weighted_score += score * weight
                total_weight += weight

            overall_score = (
                weighted_score / total_weight
                if total_weight > 0
                else 0.0
            )

            rankings.append(
                CompanyRanking(
                    rank=0,
                    company_name=company.company_name,
                    overall_score=round(
                        overall_score,
                        2,
                    ),
                    metric_scores=metric_scores,
                )
            )

        # Sort companies from highest score to lowest
        rankings.sort(
            key=lambda company: company.overall_score,
            reverse=True,
        )

        # Assign ranks
        for index, company in enumerate(rankings, start=1):
            company.rank = index

        # Generate basic grounded summary
        if rankings:
            winner = rankings[0]

            summary = (
                f"{winner.company_name} ranked first "
                f"with an overall comparison score of "
                f"{winner.overall_score} based on the "
                f"selected comparison criteria."
            )
        else:
            summary = "No companies were available for comparison."

        return ComparisonResponse(
            workspace_id=request.workspace_id,
            rankings=rankings,
            metric_comparisons=metric_comparisons,
            summary=summary,
        )