import asyncio
from crewai import Agent, Task
from crewai.tools import tool
from .processor import RedFlagProcessor

@tool
def analyze_red_flags_tool(document_id: str, company_name: str) -> str:
    """
    Triggers the complete backend red flag analysis pipeline for a given document.
    Loads extracted metrics and document chunks, runs quantitative rules,
    runs qualitative LLM analysis on risk factors and notes,
    deduplicates the findings, and stores the red flags in the database.
    Returns a summary of the detected red flags.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            result = loop.run_until_complete(RedFlagProcessor.process_red_flags(document_id, company_name))
        except RuntimeError:
            result = asyncio.run(RedFlagProcessor.process_red_flags(document_id, company_name))
            
        return result
    except Exception as e:
        return f"Red Flag pipeline failed for {document_id}: {str(e)}"

red_flag_agent = Agent(
    role="Financial Risk Analyst",
    goal="Identify potential financial risks and warning signs using validated metrics and document text.",
    backstory=(
        "You are a rigorous risk analyst. You never invent risks, but you meticulously "
        "apply rules to detect margin compression, rising debt, and qualitative warnings "
        "like auditor concerns."
    ),
    tools=[analyze_red_flags_tool],
    verbose=True,
    allow_delegation=False
)

def create_red_flag_task(document_id: str, company_name: str) -> Task:
    return Task(
        description=(
            f"Run the red flag analysis for document ID: {document_id} associated with {company_name}. "
            "Use the 'analyze_red_flags_tool' to execute the pipeline. "
            "Return the summary of the detected red flags."
        ),
        expected_output="A summary string detailing the number and severity of red flags found.",
        agent=red_flag_agent
    )
