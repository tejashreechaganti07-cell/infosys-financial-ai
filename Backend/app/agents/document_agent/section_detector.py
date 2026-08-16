import re

class SectionDetector:
    # Basic mapping of keywords to section types
    SECTION_KEYWORDS = {
        "income_statement": [r"income statement", r"statement of income", r"statement of earnings", r"statements of operations"],
        "balance_sheet": [r"balance sheet", r"statement of financial position"],
        "cash_flow_statement": [r"statement of cash flow", r"statements of cash flows"],
        "financial_notes": [r"notes to financial statements", r"notes to consolidated financial"],
        "md_and_a": [r"management's discussion and analysis", r"md&a"],
        "risk_factors": [r"risk factors"],
        "auditor_report": [r"report of independent registered public accounting firm", r"independent auditor's report"]
    }
    
    @classmethod
    def detect_section(cls, text: str) -> str:
        """
        Very naive section detector based on text content.
        In a real production system, this would use an LLM or more sophisticated NLP.
        """
        text_lower = text.lower()
        
        # Check if any keyword matches
        for section, patterns in cls.SECTION_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return section
                    
        return "unknown"
