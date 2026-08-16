import logging
from typing import List, Dict, Any
from .schemas import ExtractedMetricInput
from .exceptions import SourceVerificationFailedError

logger = logging.getLogger(__name__)

class EvidenceVerifier:
    @staticmethod
    def verify_source(metric: ExtractedMetricInput, retrieved_chunks: List[Dict[str, Any]]) -> bool:
        """
        Verifies that the chunk IDs cited by the LLM actually exist in the provided chunks.
        User specified MVP verification: (A) Source existence only.
        """
        if not metric.source_chunk_ids:
            # If no chunks cited, it's invalid unless value is None
            if metric.value is not None:
                logger.warning(f"Metric {metric.metric_name} has value but no source evidence.")
                return False
            return True
            
        valid_chunk_ids = {c["chunk_id"] for c in retrieved_chunks}
        
        for chunk_id in metric.source_chunk_ids:
            if chunk_id not in valid_chunk_ids:
                logger.error(f"Evidence chunk {chunk_id} not found in retrieved chunks for {metric.metric_name}.")
                return False
                
        return True
