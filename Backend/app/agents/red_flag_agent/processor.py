import logging
from typing import List, Dict, Any
from app.core.db import get_db
from app.agents.red_flag_agent.config import COLLECTION_EXTRACTED_METRICS, COLLECTION_DERIVED_METRICS, COLLECTION_CHUNKS
from app.agents.red_flag_agent.schemas import RedFlag
from app.agents.red_flag_agent.rules.rule_engine import QuantitativeRuleEngine
from app.agents.red_flag_agent.qualitative import QualitativeAnalyzer
from app.agents.red_flag_agent.deduplicator import Deduplicator
from app.agents.red_flag_agent.storage import RedFlagStorage
from app.agents.red_flag_agent.exceptions import RedFlagProcessingException

logger = logging.getLogger(__name__)

class RedFlagProcessor:
    @staticmethod
    async def load_metrics(document_id: str) -> List[dict]:
        db = get_db()
        metrics = []
        
        extracted = await db[COLLECTION_EXTRACTED_METRICS].find({"document_id": document_id}).to_list(length=1000)
        derived = await db[COLLECTION_DERIVED_METRICS].find({"document_id": document_id}).to_list(length=1000)
        
        metrics.extend(extracted)
        metrics.extend(derived)
        return metrics

    @staticmethod
    async def load_chunks(document_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        return await db[COLLECTION_CHUNKS].find({"document_id": document_id}).to_list(length=5000)

    @staticmethod
    async def process_red_flags(document_id: str, company_name: str = "Unknown") -> str:
        """
        Orchestrates the entire red flag pipeline.
        """
        logger.info(f"Starting Red Flag analysis for {document_id}")
        try:
            # 1. Load Data
            metrics = await RedFlagProcessor.load_metrics(document_id)
            chunks = await RedFlagProcessor.load_chunks(document_id)
            
            # 2. Run Quantitative Rules
            quant_flags: List[RedFlag] = QuantitativeRuleEngine.run_all_rules(metrics, document_id, company_name)
            
            # 3. Run Qualitative LLM Analysis
            qual_flags: List[RedFlag] = []
            try:
                qual_flags = await QualitativeAnalyzer.analyze_chunks(chunks, document_id, company_name)
            except Exception as e:
                logger.error(f"Qualitative analysis failed, continuing with quantitative only: {e}")
                
            # 4. Combine Flags
            combined_flags = quant_flags + qual_flags
            
            # 5. Deduplicate
            final_flags = Deduplicator.deduplicate(combined_flags)
            
            # 6. Store in Database
            await RedFlagStorage.save_flags(final_flags)
            
            # Count by severity for the summary
            severities = {"low": 0, "medium": 0, "high": 0}
            for f in final_flags:
                severities[f.severity] += 1
                
            summary = (
                f"Red Flag Analysis complete for {document_id}. "
                f"Found {len(final_flags)} unique flags "
                f"(High: {severities['high']}, Medium: {severities['medium']}, Low: {severities['low']})."
            )
            logger.info(summary)
            return summary
            
        except RedFlagProcessingException as e:
            logger.error(f"Red flag processing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in red flag pipeline: {e}")
            raise
