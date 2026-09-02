from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task, LLM


# ==========================================================
# LOCAL OLLAMA LLM
# ==========================================================

def create_local_llm() -> LLM:
    """
    Creates a local Ollama LLM.

    This uses the locally installed:
        llama3.2:3b

    No OpenAI API key or OpenAI credits are required.
    """

    return LLM(
        model="ollama/llama3.2:3b",
        base_url="http://localhost:11434",
        temperature=0
    )


# ==========================================================
# RED FLAG AGENT
# ==========================================================

def create_red_flag_agent() -> Agent:
    """
    Creates the CrewAI financial red flag analysis agent.
    """

    local_llm = create_local_llm()

    return Agent(
        role="Financial Red Flag Analyst",

        goal=(
            "Analyze the financial red flags supplied by the "
            "rule-based financial analysis system and produce "
            "a strictly data-grounded financial risk report."
        ),

        backstory=(
            "You are a strict financial red flag analyst. "
            "You only use information explicitly supplied in "
            "the input. You never invent numbers, causes, "
            "explanations, business facts, predictions, or "
            "recommendations."
        ),

        llm=local_llm,

        verbose=True,

        allow_delegation=False
    )


# ==========================================================
# RED FLAG TASK
# ==========================================================

def create_red_flag_task(
    agent: Agent,
    red_flags: List[Dict[str, Any]]
) -> Task:
    """
    Creates the CrewAI task using the detected red flags.
    """

    task_description = f"""
You are a STRICT financial red flag reporting agent.

The following red flags were detected by a rule-based
financial analysis system.

INPUT RED FLAGS:

{red_flags}


==================================================
ABSOLUTE DATA-GROUNDING RULES
==================================================

Use ONLY the information contained in INPUT RED FLAGS.

NEVER:

- invent numbers
- calculate percentages
- calculate new metrics
- invent causes
- invent explanations
- invent business facts
- mention customers
- mention competitors
- mention markets
- mention sales
- mention marketing
- mention pricing
- mention costs
- predict future performance
- make recommendations
- make assumptions
- change severity
- change supplied evidence
- rename risks
- add new risks
- claim company stability
- claim financial weakness unless explicitly supplied
- claim unsustainable profitability unless explicitly supplied


==================================================
RISK RULE
==================================================

For every risk:

Copy the supplied "risk" value exactly.

Do not rename it.

Do not improve it.

Do not add information to it.


==================================================
SEVERITY RULE
==================================================

Copy the supplied "severity" value exactly.

Allowed values:

HIGH
MEDIUM
LOW

Do not change them.


==================================================
EVIDENCE RULE
==================================================

Copy the supplied "evidence" value exactly.

Do not calculate anything from it.

Do not add numbers.

Do not convert numbers.

Do not create percentages.


==================================================
WHY IT MATTERS RULE
==================================================

The input may optionally contain a field called "reason".

If "reason" exists:

Copy the supplied reason exactly.

If "reason" does NOT exist:

Write EXACTLY:

"The underlying cause is not provided in the supplied data."

Do NOT create your own financial explanation.


==================================================
PRIORITY RULE
==================================================

Prioritize using ONLY severity.

HIGH = highest priority
MEDIUM = next priority
LOW = lowest priority

For equal severity, preserve the original input order.

Every input risk must receive exactly one unique priority.


==================================================
OUTPUT FORMAT
==================================================

Return ONLY this structure:

## Prioritized Financial Risks

### Priority 1
- Risk:
- Severity:
- Financial Evidence:
- Why It Matters:

### Priority 2
- Risk:
- Severity:
- Financial Evidence:
- Why It Matters:

Continue until every supplied risk has been included.


## Overall Financial Risk Assessment

State ONLY the supplied risk names and severity levels.

Do not provide financial interpretation.


## Conclusion

Write exactly ONE short sentence.

The sentence MUST be:

"The supplied financial red flags were identified."

Do not explain their causes.

Do not predict anything.

Do not make recommendations.

Do not mention company stability.


==================================================
FINAL VALIDATION
==================================================

Before returning the answer verify:

1. Every supplied risk is included.
2. No risk was added.
3. No risk was renamed.
4. Every severity is unchanged.
5. Every evidence value is unchanged.
6. No new number was created.
7. No percentage was calculated.
8. No unsupported cause was added.
9. No external financial knowledge was used.
10. Every risk has a unique priority.
11. HIGH risks appear before MEDIUM risks.
12. MEDIUM risks appear before LOW risks.
13. Equal severities preserve original order.
14. No prediction was made.
15. No recommendation was made.
16. The conclusion is exactly the required sentence.
"""

    return Task(
        description=task_description,

        expected_output=(
            "A strictly data-grounded financial red flag report "
            "containing every supplied risk, with unchanged "
            "severity and evidence, unique priorities, and "
            "no unsupported financial interpretation."
        ),

        agent=agent
    )


# ==========================================================
# ASYNC RED FLAG CREW
# ==========================================================

async def run_red_flag_crew(
    red_flags: List[Dict[str, Any]]
):
    """
    Runs the CrewAI red flag analysis asynchronously.

    Uses the local Ollama llama3.2:3b model.
    """

    if not red_flags:
        return None

    agent = create_red_flag_agent()

    task = create_red_flag_task(
        agent=agent,
        red_flags=red_flags
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = await crew.kickoff_async()

    return str(result)