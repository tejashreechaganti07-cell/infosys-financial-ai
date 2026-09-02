import os
import re
from typing import Dict, Any, Optional, List

from pypdf import PdfReader
from fastapi import HTTPException, status

from app.core.db import get_db


class ExtractionService:

    # ==========================================================
    # EXTRACT TEXT FROM PDF
    # ==========================================================

    @staticmethod
    def extract_pdf_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF file not found: {file_path}"
            )

        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF path is not a file: {file_path}"
            )

        try:
            reader = PdfReader(file_path)

            text_parts: List[str] = []

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()

                    if page_text:
                        text_parts.append(page_text)

                except Exception as page_error:
                    print(
                        f"Warning: Could not extract page "
                        f"{page_number}: {page_error}"
                    )
                    continue

            return "\n".join(text_parts)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract PDF text: {str(e)}"
            )

    # ==========================================================
    # CONVERT STRING TO NUMBER
    # ==========================================================

    @staticmethod
    def _to_number(value: Any) -> float:
        if value is None:
            return 0.0

        try:
            value = str(value).strip()

            # Remove currency symbols
            value = value.replace("₹", "")
            value = value.replace("$", "")
            value = value.replace("€", "")
            value = value.replace("£", "")

            # Remove spaces
            value = value.replace(" ", "")

            # Remove commas
            value = value.replace(",", "")

            # Handle parentheses
            # (1234) -> -1234
            if value.startswith("(") and value.endswith(")"):
                value = "-" + value[1:-1]

            # Remove trailing %
            value = value.replace("%", "")

            return float(value)

        except (ValueError, TypeError):
            return 0.0

    # ==========================================================
    # EXTRACT FIRST NUMBER MATCH
    # ==========================================================

    @staticmethod
    def _extract_number(
        text: str,
        patterns: List[str]
    ) -> Optional[float]:

        for pattern in patterns:

            try:
                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE
                )

                if match:
                    value = match.group(1)

                    if value is None:
                        continue

                    value = str(value).strip()

                    if not value:
                        continue

                    return ExtractionService._to_number(value)

            except (IndexError, ValueError, TypeError, re.error):
                continue

        return None

    # ==========================================================
    # EXTRACT TWO NUMBERS FROM FINANCIAL TABLE
    #
    # Example:
    #
    # Revenue       148819       146767
    #
    # Returns:
    # current = 148819
    # previous = 146767
    # ==========================================================

    @staticmethod
    def _extract_two_numbers(
        text: str,
        patterns: List[str]
    ) -> tuple[Optional[float], Optional[float]]:

        for pattern in patterns:

            try:
                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE
                )

                if match:

                    current = match.group(1)
                    previous = match.group(2)

                    if current and previous:

                        return (
                            ExtractionService._to_number(current),
                            ExtractionService._to_number(previous)
                        )

            except (
                IndexError,
                ValueError,
                TypeError,
                re.error
            ):
                continue

        return None, None

    # ==========================================================
    # EXTRACT FINANCIAL METRICS
    # ==========================================================

    @staticmethod
    def extract_financial_metrics(
        text: str
    ) -> Dict[str, Any]:

        financial_data: Dict[str, Any] = {}

        if not text or not text.strip():
            return financial_data

        # ------------------------------------------------------
        # Normalize text
        # ------------------------------------------------------

        text = text.replace("\u00a0", " ")
        text = text.replace("\u2013", "-")
        text = text.replace("\u2014", "-")
        text = text.replace("\u2212", "-")

        # Preserve newlines because financial tables
        # often depend on line structure
        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in text.splitlines()
            if line.strip()
        ]

        normalized_text = "\n".join(lines)

        # ======================================================
        # REVENUE
        # ======================================================

        current_revenue, previous_revenue = (
            ExtractionService._extract_two_numbers(
                normalized_text,
                [
                    r"(?:total\s+)?revenue\s*(?:from\s+operations)?"
                    r"\s*[:\-]?\s*"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)",

                    r"revenue\s+from\s+operations"
                    r"\s*[:\-]?\s*"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)",

                    r"total\s+revenue"
                    r"\s*[:\-]?\s*"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?\s*([\d,]+(?:\.\d+)?)"
                ]
            )
        )

        if current_revenue is not None:
            financial_data["revenue"] = current_revenue

        if previous_revenue is not None:
            financial_data["previous_revenue"] = previous_revenue

        # Single-value fallback
        if current_revenue is None:

            revenue = ExtractionService._extract_number(
                normalized_text,
                [
                    r"total\s+revenue\s*[:\-]?\s*[₹$€£]?"
                    r"\s*([\d,]+(?:\.\d+)?)",

                    r"revenue\s+from\s+operations\s*[:\-]?\s*[₹$€£]?"
                    r"\s*([\d,]+(?:\.\d+)?)",

                    r"\brevenue\b\s*[:\-]?\s*[₹$€£]?"
                    r"\s*([\d,]+(?:\.\d+)?)"
                ]
            )

            if revenue is not None:
                financial_data["revenue"] = revenue

        # Revenue growth
        if (
            "revenue" in financial_data
            and "previous_revenue" in financial_data
            and financial_data["previous_revenue"] != 0
        ):

            revenue_growth = (
                (
                    financial_data["revenue"]
                    - financial_data["previous_revenue"]
                )
                / abs(financial_data["previous_revenue"])
            ) * 100

            financial_data["revenue_growth"] = round(
                revenue_growth,
                2
            )

        # ======================================================
        # NET INCOME / NET PROFIT
        # ======================================================

        current_net_income, previous_net_income = (
            ExtractionService._extract_two_numbers(
                normalized_text,
                [
                    r"net\s+profit"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"net\s+income"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"profit\s+after\s+tax"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                ]
            )
        )

        if current_net_income is not None:
            financial_data["net_income"] = current_net_income

        if previous_net_income is not None:
            financial_data["previous_net_income"] = previous_net_income

        # Single-value fallback
        if current_net_income is None:

            net_income = ExtractionService._extract_number(
                normalized_text,
                [
                    r"net\s+profit\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"net\s+income\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"profit\s+after\s+tax\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                ]
            )

            if net_income is not None:
                financial_data["net_income"] = net_income

        # ======================================================
        # NET INCOME GROWTH
        # ======================================================

        if (
            "net_income" in financial_data
            and "previous_net_income" in financial_data
            and financial_data["previous_net_income"] != 0
        ):

            net_income_growth = (
                (
                    financial_data["net_income"]
                    - financial_data["previous_net_income"]
                )
                / abs(financial_data["previous_net_income"])
            ) * 100

            financial_data["net_income_growth"] = round(
                net_income_growth,
                2
            )

        # ======================================================
        # EBIT
        # ======================================================

        ebit = ExtractionService._extract_number(
            normalized_text,
            [
                r"\bEBIT\b\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)",

                r"earnings\s+before\s+interest\s+and\s+tax(?:es)?"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)"
            ]
        )

        if ebit is not None:
            financial_data["ebit"] = ebit

        # ======================================================
        # EBIT MARGIN
        # ======================================================

        ebit_margin = ExtractionService._extract_number(
            normalized_text,
            [
                r"EBIT\s+margin\s*[:\-]?\s*([\d.]+)\s*%",

                r"operating\s+margin\s*[:\-]?\s*([\d.]+)\s*%"
            ]
        )

        if ebit_margin is not None:
            financial_data["ebit_margin"] = ebit_margin

        elif (
            ebit is not None
            and "revenue" in financial_data
            and financial_data["revenue"] != 0
        ):

            financial_data["ebit_margin"] = round(
                (ebit / financial_data["revenue"]) * 100,
                2
            )

        # ======================================================
        # OPERATING CASH FLOW
        # ======================================================

        operating_cash_flow = ExtractionService._extract_number(
            normalized_text,
            [
                r"operating\s+cash\s+flow"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)",

                r"net\s+cash\s+from\s+operating\s+activities"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)",

                r"net\s+cash\s+generated\s+from\s+operating\s+activities"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)"
            ]
        )

        if operating_cash_flow is not None:
            financial_data["operating_cash_flow"] = (
                operating_cash_flow
            )

        # ======================================================
        # CAPITAL EXPENDITURE
        # ======================================================

        capital_expenditure = ExtractionService._extract_number(
            normalized_text,
            [
                r"capital\s+expenditure"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)",

                r"capital\s+expenditures"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)",

                r"purchase\s+of\s+property"
                r".{0,150}?"
                r"(-?[\d,]+(?:\.\d+)?)"
            ]
        )

        if capital_expenditure is not None:

            financial_data["capital_expenditure"] = abs(
                capital_expenditure
            )

        # ======================================================
        # FREE CASH FLOW
        # ======================================================

        free_cash_flow = ExtractionService._extract_number(
            normalized_text,
            [
                r"free\s+cash\s+flow"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*(-?[\d,]+(?:\.\d+)?)"
            ]
        )

        if free_cash_flow is not None:

            financial_data["free_cash_flow"] = (
                free_cash_flow
            )

        elif (
            "operating_cash_flow" in financial_data
            and "capital_expenditure" in financial_data
        ):

            financial_data["free_cash_flow"] = round(
                financial_data["operating_cash_flow"]
                - abs(financial_data["capital_expenditure"]),
                2
            )

        # ======================================================
        # TOTAL DEBT
        # ======================================================

        current_debt, previous_debt = (
            ExtractionService._extract_two_numbers(
                normalized_text,
                [
                    r"total\s+debt"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"total\s+borrowings"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                    r"\s+"
                    r"[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                ]
            )
        )

        if current_debt is not None:
            financial_data["total_debt"] = current_debt

        if previous_debt is not None:
            financial_data["previous_total_debt"] = previous_debt

        if current_debt is None:

            total_debt = ExtractionService._extract_number(
                normalized_text,
                [
                    r"total\s+debt"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)",

                    r"total\s+borrowings"
                    r"\s*[:\-]?\s*[₹$€£]?"
                    r"\s*(-?[\d,]+(?:\.\d+)?)"
                ]
            )

            if total_debt is not None:
                financial_data["total_debt"] = total_debt

        # ======================================================
        # DEBT GROWTH
        # ======================================================

        if (
            "total_debt" in financial_data
            and "previous_total_debt" in financial_data
            and financial_data["previous_total_debt"] != 0
        ):

            debt_growth = (
                (
                    financial_data["total_debt"]
                    - financial_data["previous_total_debt"]
                )
                / abs(financial_data["previous_total_debt"])
            ) * 100

            financial_data["debt_growth"] = round(
                debt_growth,
                2
            )

        # ======================================================
        # SHAREHOLDERS' EQUITY
        # ======================================================

        shareholders_equity = ExtractionService._extract_number(
            normalized_text,
            [
                r"shareholders[’']?\s+equity"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*([\d,]+(?:\.\d+)?)",

                r"total\s+equity"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*([\d,]+(?:\.\d+)?)",

                r"equity\s+attributable\s+to\s+owners"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*([\d,]+(?:\.\d+)?)"
            ]
        )

        if shareholders_equity is not None:
            financial_data["shareholders_equity"] = (
                shareholders_equity
            )

        # ======================================================
        # DEBT TO EQUITY
        # ======================================================

        debt_to_equity = ExtractionService._extract_number(
            normalized_text,
            [
                r"debt[-\s]+to[-\s]+equity"
                r"\s*[:\-]?\s*([\d.]+)",

                r"debt\s*/\s*equity"
                r"\s*[:\-]?\s*([\d.]+)"
            ]
        )

        if debt_to_equity is not None:

            financial_data["debt_to_equity"] = (
                debt_to_equity
            )

        elif (
            "total_debt" in financial_data
            and "shareholders_equity" in financial_data
            and financial_data["shareholders_equity"] != 0
        ):

            financial_data["debt_to_equity"] = round(
                financial_data["total_debt"]
                / financial_data["shareholders_equity"],
                4
            )

        # ======================================================
        # CURRENT ASSETS
        # ======================================================

        current_assets = ExtractionService._extract_number(
            normalized_text,
            [
                r"current\s+assets"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*([\d,]+(?:\.\d+)?)"
            ]
        )

        if current_assets is not None:
            financial_data["current_assets"] = current_assets

        # ======================================================
        # CURRENT LIABILITIES
        # ======================================================

        current_liabilities = ExtractionService._extract_number(
            normalized_text,
            [
                r"current\s+liabilities"
                r"\s*[:\-]?\s*[₹$€£]?"
                r"\s*([\d,]+(?:\.\d+)?)"
            ]
        )

        if current_liabilities is not None:
            financial_data["current_liabilities"] = (
                current_liabilities
            )

        # ======================================================
        # CURRENT RATIO
        # ======================================================

        if (
            "current_assets" in financial_data
            and "current_liabilities" in financial_data
            and financial_data["current_liabilities"] != 0
        ):

            financial_data["current_ratio"] = round(
                financial_data["current_assets"]
                / financial_data["current_liabilities"],
                2
            )

        # ======================================================
        # PRINT EXTRACTED DATA FOR DEBUGGING
        # ======================================================

        print("\n" + "=" * 60)
        print("EXTRACTED FINANCIAL DATA")
        print("=" * 60)

        for key, value in financial_data.items():
            print(f"{key:30}: {value}")

        print("=" * 60 + "\n")

        return financial_data

    # ==========================================================
    # EXTRACT DOCUMENT
    # ==========================================================

    @staticmethod
    async def extract_document(
        user_id: str,
        document_id: str
    ) -> Dict[str, Any]:

        db = get_db()

        docs_col = db["documents"]

        # ======================================================
        # FIND DOCUMENT
        # ======================================================

        document = await docs_col.find_one(
            {
                "user_id": user_id,
                "$or": [
                    {"_id": document_id},
                    {"id": document_id}
                ]
            }
        )

        if not document:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )

        # ======================================================
        # GET FILE PATH
        # ======================================================

        relative_path = document.get("file_path")

        if not relative_path:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document does not contain a file path"
            )

        # ======================================================
        # FIND APP DIRECTORY
        # ======================================================

        app_directory = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ======================================================
        # BUILD ABSOLUTE FILE PATH
        # ======================================================

        # Normalize Windows path separators
        relative_path = relative_path.replace("\\", os.sep)
        relative_path = relative_path.replace("/", os.sep)

        file_path = os.path.abspath(
            os.path.join(
                app_directory,
                relative_path
            )
        )

        # ======================================================
        # DEBUG
        # ======================================================

        print("\n" + "=" * 60)
        print("DOCUMENT EXTRACTION")
        print("=" * 60)

        print(f"Document ID    : {document_id}")
        print(f"Relative path  : {relative_path}")
        print(f"Absolute path  : {file_path}")
        print(f"File exists    : {os.path.exists(file_path)}")

        print("=" * 60 + "\n")

        # ======================================================
        # EXTRACT PDF TEXT
        # ======================================================

        text = ExtractionService.extract_pdf_text(
            file_path
        )

        if not text.strip():

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No text could be extracted from this PDF. "
                    "The PDF may contain scanned images."
                )
            )

        # ======================================================
        # EXTRACT FINANCIAL METRICS
        # ======================================================

        financial_data = (
            ExtractionService.extract_financial_metrics(
                text
            )
        )

        # ======================================================
        # RETURN RESULT
        # ======================================================

        return {
            "document_id": document_id,

            "document_name": document.get(
                "title"
            ),

            "company_name": document.get(
                "company_name"
            ),

            "filing_type": document.get(
                "filing_type"
            ),

            "fiscal_year": document.get(
                "fiscal_year"
            ),

            "text_length": len(text),

            "financial_data": financial_data,

            "message": (
                "Document extraction completed successfully"
            )
        }