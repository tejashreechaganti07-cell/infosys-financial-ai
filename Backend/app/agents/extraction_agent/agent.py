import asyncio
from crewai import Agent, Task
from crewai.tools import tool
from .processor import ExtractionProcessor

@tool
def extract_financial_metrics_tool(document_id: str, company_name: str) -> str:
    """
    Triggers the complete backend extraction pipeline for a given document.
    Retrieves parsed chunks, executes LLM extraction for all required metrics,
    normalizes the values, verifies evidence, calculates derived metrics,
    and stores everything in the database.
    Returns a summary of the extracted metrics.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            result = loop.run_until_complete(ExtractionProcessor.process_extraction(document_id, company_name))
        except RuntimeError:
            result = asyncio.run(ExtractionProcessor.process_extraction(document_id, company_name))
            
        return result
    except Exception as e:
        return f"Extraction pipeline failed for {document_id}: {str(e)}"

extraction_agent = Agent(
    role="Financial Extraction Specialist",
    goal="Extract and validate financial metrics from document chunks without hallucinating.",
    backstory=(
        "You are an expert financial analyst. Your job is to extract exact financial "
        "figures from company reports. You never guess or invent numbers. You rely purely "
        "on the structured extraction tool provided to you."
    ),
    tools=[extract_financial_metrics_tool],
    verbose=True,
    allow_delegation=False
)

def create_extraction_task(document_id: str, company_name: str) -> Task:
    return Task(
        description=(
            f"Extract financial metrics for the document ID: {document_id} associated with {company_name}. "
            "Use the 'extract_financial_metrics_tool' to run the extraction pipeline. "
            "Return the summary of the extracted metrics."
        ),
        expected_output="A summary string confirming successful extraction of direct and derived metrics.",
        agent=extraction_agent
    )
