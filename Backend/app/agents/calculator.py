from typing import Optional


def calculate_ratio(
    numerator: Optional[float],
    denominator: Optional[float]
) -> Optional[float]:
    """
    Safely calculate a ratio.
    Returns None if calculation is not possible.
    """

    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def calculate_financial_metrics(metrics: dict) -> dict:
    """
    Calculate financial ratios from extracted metrics.

    Expected input example:

    {
        "revenue": 2500000000,
        "gross_profit": 1000000000,
        "operating_income": 500000000,
        "net_income": 400000000,
        "current_assets": 800000000,
        "current_liabilities": 400000000,
        "total_debt": 600000000,
        "total_equity": 1200000000
    }
    """

    revenue = metrics.get("revenue")
    gross_profit = metrics.get("gross_profit")
    operating_income = metrics.get("operating_income")
    net_income = metrics.get("net_income")

    current_assets = metrics.get("current_assets")
    current_liabilities = metrics.get("current_liabilities")

    total_debt = metrics.get("total_debt")
    total_equity = metrics.get("total_equity")

    calculated_metrics = {
        "gross_margin": calculate_ratio(
            gross_profit,
            revenue
        ),

        "operating_margin": calculate_ratio(
            operating_income,
            revenue
        ),

        "net_profit_margin": calculate_ratio(
            net_income,
            revenue
        ),

        "current_ratio": calculate_ratio(
            current_assets,
            current_liabilities
        ),

        "debt_to_equity": calculate_ratio(
            total_debt,
            total_equity
        )
    }

    return calculated_metrics