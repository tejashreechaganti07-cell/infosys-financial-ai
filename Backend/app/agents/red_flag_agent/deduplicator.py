from typing import List
import logging
from app.agents.red_flag_agent.schemas import RedFlag

logger = logging.getLogger(__name__)

class Deduplicator:
    @staticmethod
    def deduplicate(flags: List[RedFlag]) -> List[RedFlag]:
        """
        Rule-based deduplication: If same document + same category + same flag_type exist, 
        merge them or keep the highest severity one.
        """
        severity_rank = {"low": 1, "medium": 2, "high": 3}
        
        unique_flags = {}
        for flag in flags:
            key = (flag.document_id, flag.category, flag.flag_type)
            
            if key not in unique_flags:
                unique_flags[key] = flag
            else:
                existing = unique_flags[key]
                # If we found a duplicate, keep the one with higher severity
                if severity_rank.get(flag.severity, 1) > severity_rank.get(existing.severity, 1):
                    # Combine evidence chunk IDs
                    flag.source_chunk_ids = list(set(flag.source_chunk_ids + existing.source_chunk_ids))
                    flag.detected_metrics = list(set(flag.detected_metrics + existing.detected_metrics))
                    unique_flags[key] = flag
                else:
                    existing.source_chunk_ids = list(set(flag.source_chunk_ids + existing.source_chunk_ids))
                    existing.detected_metrics = list(set(flag.detected_metrics + existing.detected_metrics))
                    
        logger.info(f"Deduplicated {len(flags)} flags down to {len(unique_flags)} flags.")
        return list(unique_flags.values())
