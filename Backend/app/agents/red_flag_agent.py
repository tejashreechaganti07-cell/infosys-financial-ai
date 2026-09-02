from crewai import Agent, LLM


def create_red_flag_agent() -> Agent:

    llm = LLM(
        model="ollama/llama3.2:3b",
        base_url="http://localhost:11434"
    )

    return Agent(
        role="Financial Red Flag Analyst",

        goal=(
            "Analyze financial red flags detected by the financial "
            "analysis service, explain their significance, prioritize "
            "the risks, and provide a professional overall risk assessment "
            "using only the supplied financial data."
        ),

        backstory=(
            "You are a financial risk analyst specializing in financial "
            "statement analysis. You evaluate revenue trends, "
            "profitability, leverage, cash flow, and liquidity. "
            "You identify the most serious risks, explain why they matter, "
            "and prioritize them clearly. You never invent financial "
            "numbers, facts, or information that was not provided."
        ),

        llm=llm,
        verbose=True,
        allow_delegation=False
    )