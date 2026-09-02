from typing import Dict, Any, List


class RedFlagService:

    @staticmethod
    def calculate_percentage_change(
        current: float,
        previous: float
    ) -> float:
        """Calculate percentage change between two values."""

        if previous == 0:
            return 0.0

        return round(
            ((current - previous) / abs(previous)) * 100,
            2
        )

    @staticmethod
    def analyze_financial_data(
        current_data: Dict[str, Any],
        previous_data: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:

        red_flags: List[Dict[str, Any]] = []

        previous_data = previous_data or {}

        # --------------------------------------------------
        # 1. REVENUE DECLINE
        # --------------------------------------------------
        if "revenue" in current_data and "revenue" in previous_data:

            current = float(current_data["revenue"])
            previous = float(previous_data["revenue"])

            change = RedFlagService.calculate_percentage_change(
                current,
                previous
            )

            if change <= -20:
                red_flags.append({
                    "category": "Revenue",
                    "metric": "Revenue",
                    "severity": "HIGH",
                    "change_percentage": change,
                    "message": f"Revenue declined by {abs(change)}%."
                })

            elif change <= -10:
                red_flags.append({
                    "category": "Revenue",
                    "metric": "Revenue",
                    "severity": "MEDIUM",
                    "change_percentage": change,
                    "message": f"Revenue declined by {abs(change)}%."
                })

        # --------------------------------------------------
        # 2. NET PROFIT DECLINE
        # --------------------------------------------------
        if "net_income" in current_data and "net_income" in previous_data:

            current = float(current_data["net_income"])
            previous = float(previous_data["net_income"])

            change = RedFlagService.calculate_percentage_change(
                current,
                previous
            )

            if change <= -30:
                red_flags.append({
                    "category": "Profitability",
                    "metric": "Net Income",
                    "severity": "HIGH",
                    "change_percentage": change,
                    "message": f"Net income declined by {abs(change)}%."
                })

            elif change <= -15:
                red_flags.append({
                    "category": "Profitability",
                    "metric": "Net Income",
                    "severity": "MEDIUM",
                    "change_percentage": change,
                    "message": f"Net income declined by {abs(change)}%."
                })

        # --------------------------------------------------
        # 3. DEBT INCREASE
        # --------------------------------------------------
        if "total_debt" in current_data and "total_debt" in previous_data:

            current = float(current_data["total_debt"])
            previous = float(previous_data["total_debt"])

            change = RedFlagService.calculate_percentage_change(
                current,
                previous
            )

            if change >= 50:
                red_flags.append({
                    "category": "Leverage",
                    "metric": "Total Debt",
                    "severity": "HIGH",
                    "change_percentage": change,
                    "message": f"Total debt increased by {change}%."
                })

            elif change >= 25:
                red_flags.append({
                    "category": "Leverage",
                    "metric": "Total Debt",
                    "severity": "MEDIUM",
                    "change_percentage": change,
                    "message": f"Total debt increased by {change}%."
                })

        # --------------------------------------------------
        # 4. NEGATIVE OPERATING CASH FLOW
        # --------------------------------------------------
        if "operating_cash_flow" in current_data:

            cash_flow = float(current_data["operating_cash_flow"])

            if cash_flow < 0:
                red_flags.append({
                    "category": "Cash Flow",
                    "metric": "Operating Cash Flow",
                    "severity": "HIGH",
                    "change_percentage": None,
                    "message": "Operating cash flow is negative."
                })

        # --------------------------------------------------
        # 5. CURRENT RATIO / LIQUIDITY
        # --------------------------------------------------
        if (
            "current_assets" in current_data
            and "current_liabilities" in current_data
        ):

            assets = float(current_data["current_assets"])
            liabilities = float(current_data["current_liabilities"])

            if liabilities != 0:

                current_ratio = round(
                    assets / liabilities,
                    2
                )

                if current_ratio < 1:

                    red_flags.append({
                        "category": "Liquidity",
                        "metric": "Current Ratio",
                        "severity": "HIGH",
                        "value": current_ratio,
                        "message": (
                            f"Current ratio is {current_ratio}, "
                            "indicating potential liquidity risk."
                        )
                    })

                elif current_ratio < 1.5:

                    red_flags.append({
                        "category": "Liquidity",
                        "metric": "Current Ratio",
                        "severity": "MEDIUM",
                        "value": current_ratio,
                        "message": (
                            f"Current ratio is {current_ratio}, "
                            "which indicates weaker liquidity."
                        )
                    })

        # --------------------------------------------------
        # 6. RISK SCORE
        # --------------------------------------------------

        risk_score = 0

        for flag in red_flags:

            if flag["severity"] == "HIGH":
                risk_score += 30

            elif flag["severity"] == "MEDIUM":
                risk_score += 15

            elif flag["severity"] == "LOW":
                risk_score += 5

        # Maximum score = 100
        risk_score = min(risk_score, 100)

        # --------------------------------------------------
        # 7. OVERALL RISK
        # --------------------------------------------------

        if risk_score >= 75:
            overall_risk = "CRITICAL"

        elif risk_score >= 50:
            overall_risk = "HIGH"

        elif risk_score >= 25:
            overall_risk = "MEDIUM"

        else:
            overall_risk = "LOW"

        # --------------------------------------------------
        # 8. RETURN RESULT
        # --------------------------------------------------

        return {
            "risk_score": risk_score,
            "overall_risk": overall_risk,
            "red_flags_count": len(red_flags),
            "red_flags": red_flags
        }


# ==========================================================
# TEST THE RED FLAG SERVICE
# ==========================================================

if __name__ == "__main__":

    current_data = {
        "revenue": 7000,
        "net_income": 500,
        "total_debt": 4500,
        "operating_cash_flow": -200,
        "current_assets": 3000,
        "current_liabilities": 4000
    }

    previous_data = {
        "revenue": 10000,
        "net_income": 1000,
        "total_debt": 2000
    }

    result = RedFlagService.analyze_financial_data(
        current_data,
        previous_data
    )

    print("\n========== RED FLAG ANALYSIS ==========")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Overall Risk: {result['overall_risk']}")
    print(f"Red Flags Found: {result['red_flags_count']}")

    print("\nDetected Red Flags:")

    for flag in result["red_flags"]:
        print(
            f"- [{flag['severity']}] "
            f"{flag['category']}: "
            f"{flag['message']}"
        )