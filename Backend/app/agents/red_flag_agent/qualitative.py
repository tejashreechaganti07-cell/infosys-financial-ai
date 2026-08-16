import logging
import uuid
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.agents.red_flag_agent.schemas import RedFlag, QualitativeFlagInput
from app.agents.red_flag_agent.prompts import SYSTEM_QUALITATIVE_PROMPT, USER_QUALITATIVE_PROMPT
from app.agents.red_flag_agent.config import LLM_MODEL
from app.agents.red_flag_agent.exceptions import QualitativeAnalysisError

logger = logging.getLogger(__name__)

class LLMQualitativeResponse(BaseModel):
    potential_flags: List[QualitativeFlagInput] = Field(description="List of identified qualitative flags.")

class QualitativeAnalyzer:
    @staticmethod
    async def analyze_chunks(chunks: List[Dict], document_id: str, company_name: str) -> List[RedFlag]:
        """
        Runs LLM over provided document chunks to identify qualitative risks.
        """
        # Filter chunks that are likely to contain qualitative risks
        target_sections = {"md_and_a", "financial_notes", "auditor_report", "risk_factors", "unknown"}
        relevant_chunks = [c for c in chunks if c.get("section_type") in target_sections]
        
        if not relevant_chunks:
            logger.info("No relevant chunks found for qualitative analysis.")
            return []
            
        try:
            # Prepare context string (limit chunk size to avoid context overflow if needed)
            context_blocks = []
            for c in relevant_chunks[:20]: # hard limit for safety
                context_blocks.append(
                    f"--- CHUNK {c['chunk_id']} ---\n"
                    f"Section: {c.get('section_type')}\n"
                    f"Text:\n{c.get('text')}\n"
                )
            context_str = "\n".join(context_blocks)
            
            llm = ChatOpenAI(model=LLM_MODEL, temperature=0.0)
            structured_llm = llm.with_structured_output(LLMQualitativeResponse)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_QUALITATIVE_PROMPT),
                ("user", USER_QUALITATIVE_PROMPT)
            ])
            
            chain = prompt | structured_llm
            logger.info(f"Running Qualitative LLM analysis for {document_id}")
            
            response: LLMQualitativeResponse = await chain.ainvoke({"context": context_str})
            
            # Convert to RedFlag objects
            flags = []
            for qf in response.potential_flags:
                flags.append(RedFlag(
                    flag_id=f"flag_{uuid.uuid4().hex[:8]}",
                    document_id=document_id,
                    company_name=company_name,
                    flag_type=qf.category.lower().replace(" ", "_"),
                    category="qualitative",
                    severity=qf.severity.lower(),
                    title=qf.title,
                    description=qf.description,
                    source_chunk_ids=qf.source_chunk_ids,
                    confidence_score=qf.confidence_score
                ))
            return flags
            
        except Exception as e:
            logger.error(f"Qualitative analysis failed: {e}")
            raise QualitativeAnalysisError(f"LLM failure: {e}")
