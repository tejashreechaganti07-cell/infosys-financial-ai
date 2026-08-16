import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from .schemas import ExtractedMetricInput
from .prompts import SYSTEM_EXTRACTION_PROMPT, USER_EXTRACTION_PROMPT
from .config import LLM_MODEL
from .exceptions import LLMServiceError

logger = logging.getLogger(__name__)

class LLMExtractionResponse(BaseModel):
    """Wrapper schema because a metric might have multiple fiscal years."""
    metrics: List[ExtractedMetricInput] = Field(description="List of extracted metrics for each fiscal year found.")

class MetricExtractor:
    @classmethod
    async def extract_metric(cls, metric_name: str, chunks: List[Dict[str, Any]]) -> List[ExtractedMetricInput]:
        """
        Calls the LLM to extract the metric from the provided chunks.
        Returns a list of ExtractedMetricInput (one per fiscal year found).
        """
        if not chunks:
            return []
            
        try:
            # Prepare context string
            context_blocks = []
            for idx, c in enumerate(chunks, 1):
                context_blocks.append(
                    f"--- CHUNK {idx} ---\n"
                    f"ID: {c['chunk_id']}\n"
                    f"Page: {c['page_number']}\n"
                    f"Section: {c['section_type']}\n"
                    f"Text:\n{c['text']}\n"
                )
            context_str = "\n".join(context_blocks)
            
            # Initialize LLM with structured output
            llm = ChatOpenAI(model=LLM_MODEL, temperature=0.0)
            structured_llm = llm.with_structured_output(LLMExtractionResponse)
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_EXTRACTION_PROMPT),
                ("user", USER_EXTRACTION_PROMPT)
            ])
            
            chain = prompt | structured_llm
            
            logger.info(f"Calling LLM ({LLM_MODEL}) for metric: {metric_name}")
            response: LLMExtractionResponse = await chain.ainvoke({
                "metric_name": metric_name,
                "context": context_str
            })
            
            return response.metrics
            
        except Exception as e:
            logger.error(f"LLM Extraction failed for {metric_name}: {e}")
            raise LLMServiceError(f"Failed to extract metric via LLM: {e}")
