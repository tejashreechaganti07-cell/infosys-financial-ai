from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.services.red_flag_service import RedFlagService
from app.crew.red_flag_crew import run_red_flag_crew


router = APIRouter(
    prefix="/red-flags",
    tags=["Red Flags"]
)


@router.post("/analyze")
async def analyze_red_flags(data: Dict[str, Any]):
    """
    Analyze financial data using rule-based red flag detection
    and CrewAI.
    """

    try:
        # --------------------------------------------------
        # Accept either:
        #
        # {
        #   "current_data": {...},
        #   "previous_data": {...}
        # }
        #
        # OR direct financial data:
        #
        # {
        #   "revenue": 80000,
        #   ...
        # }
        # --------------------------------------------------

        if "current_data" in data:

            current_data = data.get("current_data", {})
            previous_data = data.get("previous_data", {})

        else:

            # Direct financial data is treated as current data
            current_data = data
            previous_data = {}

        if not isinstance(current_data, dict):
            raise HTTPException(
                status_code=400,
                detail="current_data must be an object."
            )

        if not isinstance(previous_data, dict):
            raise HTTPException(
                status_code=400,
                detail="previous_data must be an object."
            )

        # --------------------------------------------------
        # Rule-based analysis
        # --------------------------------------------------

        result = RedFlagService.analyze_financial_data(
            current_data=current_data,
            previous_data=previous_data
        )

        red_flags = result["red_flags"]

        # --------------------------------------------------
        # CrewAI analysis
        # --------------------------------------------------

        ai_analysis = None

        if red_flags:
            try:
                ai_analysis = await run_red_flag_crew(red_flags)
            except Exception as e:
                print("CrewAI error:", str(e))
                ai_analysis = None

        # --------------------------------------------------
        # Return response
        # --------------------------------------------------

        return {
            "success": True,
            "risk_score": result["risk_score"],
            "overall_risk": result["overall_risk"],
            "red_flags": red_flags,
            "count": len(red_flags),
            "ai_analysis": ai_analysis
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n========================================")
        print("RED FLAG ANALYSIS ERROR")
        print("========================================")
        print(str(e))
        print("========================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Red flag analysis failed: {str(e)}"
        )