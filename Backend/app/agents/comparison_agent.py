import json
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.core.db import get_db


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

COLLECTION_EXTRACTED = "extracted_metrics"
COLLECTION_COMPARISONS = "comparisons"


# ============================================================
# OUTPUT SCHEMAS
# ============================================================

class ComparisonItem(BaseModel):
    metric_name: str

    subject_value: Optional[float] = None

    benchmark_value: Optional[float] = None

    benchmark_type: str = "historical"

    benchmark_source: Optional[str] = None

    absolute_difference: Optional[float] = None

    percentage_difference: Optional[float] = None

    performance: str = "NOT_AVAILABLE"

    explanation: Optional[str] = None


class ComparisonOutput(BaseModel):
    document_id: str

    company_name: str

    comparisons: List[ComparisonItem] = Field(
        default_factory=list
    )

    total_metrics_compared: int = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_historical_data(
    historical_data: Optional[
        Union[str, Dict[str, Any]]
    ]
) -> Dict[str, Any]:
    """
    Accept historical/peer data as either:

    Dictionary:
    {
        "Revenue": 100000,
        "Net Income": {
            "value": 5000,
            "source": "Industry Average"
        }
    }

    Or JSON string containing the same structure.
    """

    if not historical_data:
        return {}

    if isinstance(historical_data, dict):
        return historical_data

    if isinstance(historical_data, str):

        try:
            parsed = json.loads(
                historical_data
            )

            if isinstance(parsed, dict):
                return parsed

            return {}

        except json.JSONDecodeError:

            logger.warning(
                "Historical data is not valid JSON"
            )

            return {}

    return {}


def get_benchmark_details(
    benchmark_data: Any
) -> Dict[str, Any]:
    """
    Convert benchmark input into a consistent structure.
    """

    # Simple format:
    #
    # "Revenue": 100000

    if isinstance(
        benchmark_data,
        (int, float)
    ):
        return {
            "value": float(
                benchmark_data
            ),
            "source": "Historical Data",
            "type": "historical"
        }

    # Detailed format:
    #
    # "Revenue": {
    #     "value": 100000,
    #     "source": "FY 2023",
    #     "type": "historical"
    # }

    if isinstance(
        benchmark_data,
        dict
    ):

        value = benchmark_data.get(
            "value"
        )

        if value is None:
            return {
                "value": None,
                "source": None,
                "type": "historical"
            }

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            value = None

        return {
            "value": value,

            "source": benchmark_data.get(
                "source",
                "Benchmark Data"
            ),

            "type": benchmark_data.get(
                "type",
                "historical"
            )
        }

    return {
        "value": None,
        "source": None,
        "type": "historical"
    }


def calculate_percentage_difference(
    subject_value: float,
    benchmark_value: float
) -> Optional[float]:

    if benchmark_value == 0:
        return None

    return round(
        (
            (
                subject_value
                -
                benchmark_value
            )
            /
            abs(
                benchmark_value
            )
        )
        *
        100,
        2
    )


def determine_performance(
    difference_percentage: Optional[float]
) -> str:
    """
    Simple comparison classification.
    """

    if difference_percentage is None:
        return "NOT_AVAILABLE"

    if difference_percentage > 5:
        return "ABOVE_BENCHMARK"

    if difference_percentage < -5:
        return "BELOW_BENCHMARK"

    return "IN_LINE_WITH_BENCHMARK"


# ============================================================
# COMPARISON PROCESSOR
# ============================================================

class ComparisonProcessor:

    @staticmethod
    async def process_comparison(

        document_id: str,

        company_name: str = "Unknown",

        historical_data: Optional[
            Union[str, Dict[str, Any]]
        ] = None

    ) -> ComparisonOutput:

        logger.info(
            "Starting Comparison Agent for %s",
            document_id
        )

        db = get_db()

        extracted_collection = db[
            COLLECTION_EXTRACTED
        ]

        comparison_collection = db[
            COLLECTION_COMPARISONS
        ]


        # ----------------------------------------------------
        # STEP 1
        # RETRIEVE EXTRACTED METRICS
        # ----------------------------------------------------

        extracted_metrics = []

        cursor = extracted_collection.find(
            {
                "document_id": document_id
            }
        )

        async for metric in cursor:

            extracted_metrics.append(
                metric
            )


        if not extracted_metrics:

            logger.warning(
                "No extracted metrics found for "
                "document %s",
                document_id
            )

            return ComparisonOutput(

                document_id=document_id,

                company_name=company_name,

                comparisons=[],

                total_metrics_compared=0
            )


        # ----------------------------------------------------
        # STEP 2
        # NORMALIZE BENCHMARK DATA
        # ----------------------------------------------------

        benchmarks = normalize_historical_data(
            historical_data
        )


        comparisons = []


        # ----------------------------------------------------
        # STEP 3
        # COMPARE EACH METRIC
        # ----------------------------------------------------

        for metric in extracted_metrics:

            metric_name = metric.get(
                "metric_name"
            )

            subject_value = metric.get(
                "value"
            )


            if (
                metric_name is None
                or
                subject_value is None
            ):
                continue


            try:

                subject_value = float(
                    subject_value
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            # Find matching benchmark

            benchmark_raw = benchmarks.get(
                metric_name
            )


            # If no benchmark exists,
            # include metric but mark unavailable

            if benchmark_raw is None:

                comparison = ComparisonItem(

                    metric_name=metric_name,

                    subject_value=subject_value,

                    benchmark_value=None,

                    benchmark_type="NOT_PROVIDED",

                    benchmark_source=None,

                    absolute_difference=None,

                    percentage_difference=None,

                    performance="BENCHMARK_NOT_AVAILABLE",

                    explanation=(
                        f"No historical or peer "
                        f"benchmark was provided for "
                        f"{metric_name}."
                    )
                )

                comparisons.append(
                    comparison
                )

                continue


            # ------------------------------------------------
            # GET BENCHMARK DETAILS
            # ------------------------------------------------

            benchmark = get_benchmark_details(
                benchmark_raw
            )

            benchmark_value = benchmark.get(
                "value"
            )


            if benchmark_value is None:

                comparison = ComparisonItem(

                    metric_name=metric_name,

                    subject_value=subject_value,

                    benchmark_value=None,

                    benchmark_type=benchmark.get(
                        "type",
                        "historical"
                    ),

                    benchmark_source=benchmark.get(
                        "source"
                    ),

                    performance="BENCHMARK_NOT_AVAILABLE",

                    explanation=(
                        f"Benchmark value for "
                        f"{metric_name} "
                        f"is invalid or missing."
                    )
                )

                comparisons.append(
                    comparison
                )

                continue


            # ------------------------------------------------
            # CALCULATIONS
            # ------------------------------------------------

            absolute_difference = round(

                subject_value
                -
                benchmark_value,

                2
            )


            percentage_difference = (
                calculate_percentage_difference(

                    subject_value,

                    benchmark_value
                )
            )


            performance = (
                determine_performance(
                    percentage_difference
                )
            )


            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            if percentage_difference is None:

                explanation = (
                    f"{metric_name} could not be "
                    f"percentage-compared because "
                    f"the benchmark value is zero."
                )

            elif performance == "ABOVE_BENCHMARK":

                explanation = (
                    f"{metric_name} is "
                    f"{abs(percentage_difference)}% "
                    f"above the benchmark."
                )

            elif performance == "BELOW_BENCHMARK":

                explanation = (
                    f"{metric_name} is "
                    f"{abs(percentage_difference)}% "
                    f"below the benchmark."
                )

            else:

                explanation = (
                    f"{metric_name} is broadly "
                    f"in line with the benchmark."
                )


            comparison = ComparisonItem(

                metric_name=metric_name,

                subject_value=subject_value,

                benchmark_value=benchmark_value,

                benchmark_type=benchmark.get(
                    "type",
                    "historical"
                ),

                benchmark_source=benchmark.get(
                    "source"
                ),

                absolute_difference=(
                    absolute_difference
                ),

                percentage_difference=(
                    percentage_difference
                ),

                performance=performance,

                explanation=explanation
            )


            comparisons.append(
                comparison
            )


        # ----------------------------------------------------
        # STEP 4
        # CREATE OUTPUT
        # ----------------------------------------------------

        output = ComparisonOutput(

            document_id=document_id,

            company_name=company_name,

            comparisons=comparisons,

            total_metrics_compared=len(
                [
                    comparison
                    for comparison in comparisons
                    if comparison.benchmark_value
                    is not None
                ]
            )
        )


        # ----------------------------------------------------
        # STEP 5
        # STORE RESULT
        # ----------------------------------------------------

        comparison_document = {

            "document_id": document_id,

            "company_name": company_name,

            "comparisons": [

                comparison.model_dump()

                for comparison
                in output.comparisons
            ],

            "total_metrics_compared":
                output.total_metrics_compared
        }


        # Remove old comparison result
        # for the same document

        await comparison_collection.delete_many(
            {
                "document_id": document_id
            }
        )


        # Store new result

        await comparison_collection.insert_one(
            comparison_document
        )


        logger.info(

            "Comparison Agent completed for %s. "
            "Compared %s metrics.",

            document_id,

            output.total_metrics_compared
        )


        return output