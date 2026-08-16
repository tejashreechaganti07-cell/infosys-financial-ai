import uuid
import logging
from datetime import datetime
from typing import List
from .config import REQUIRED_METRICS
from .schemas import ValidatedMetric, ExtractedMetricInput
from .retriever import HybridRetriever
from .extractor import MetricExtractor
from .normalizer import ValueNormalizer
from .evidence import EvidenceVerifier
from .calculator import DeterministicCalculator
from .storage import ExtractionStorage
from .exceptions import ExtractionProcessingException

logger = logging.getLogger(__name__)

class ExtractionProcessor:
    @staticmethod
    async def process_extraction(document_id: str, company_name: str = "Unknown") -> str:
        """
        Orchestrates the entire extraction pipeline for a single document.
        """
        logger.info(f"Starting extraction for document {document_id}")
        
        all_validated_metrics: List[ValidatedMetric] = []
        
        try:
            # 1. Loop through all required direct metrics
            for metric_name in REQUIRED_METRICS:
                logger.info(f"Processing metric: {metric_name}")
                
                # Retrieve context chunks
                chunks = await HybridRetriever.retrieve_chunks(document_id, metric_name)
                
                if not chunks:
                    logger.warning(f"No relevant chunks found for {metric_name}")
                    continue
                    
                # LLM Extraction
                extracted_results: List[ExtractedMetricInput] = await MetricExtractor.extract_metric(metric_name, chunks)
                
                for extracted in extracted_results:
                    if extracted.value is None:
                        # Metric not found in context
                        continue
                        
                    # Validate Evidence
                    is_valid_evidence = EvidenceVerifier.verify_source(extracted, chunks)
                    status = "extracted" if is_valid_evidence else "validation_failed"
                    
                    # Normalize values
                    norm_val, norm_unit = ValueNormalizer.normalize(
                        extracted.value, 
                        extracted.original_value, 
                        extracted.unit
                    )
                    
                    # Build Validated Metric
                    val_metric = ValidatedMetric(
                        metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                        document_id=document_id,
                        company_name=company_name,
                        metric_name=metric_name,
                        fiscal_year=extracted.fiscal_year,
                        value=norm_val,
                        original_value=extracted.original_value,
                        currency=extracted.currency,
                        unit=norm_unit,
                        source_type="extracted",
                        source_chunk_ids=extracted.source_chunk_ids,
                        source_pages=extracted.source_pages,
                        confidence_score=extracted.confidence_score,
                        status=status,
                        created_at=datetime.utcnow().isoformat()
                    )
                    all_validated_metrics.append(val_metric)

            # 2. Store extracted metrics
            await ExtractionStorage.save_extracted_metrics(all_validated_metrics)
            
            # 3. Calculate Derived Metrics deterministically
            derived_metrics = DeterministicCalculator.calculate_derived_metrics(
                document_id, company_name, all_validated_metrics
            )
            
            # 4. Store Derived Metrics
            await ExtractionStorage.save_derived_metrics(derived_metrics)
            
            return (
                f"Successfully extracted {len(all_validated_metrics)} direct metrics "
                f"and calculated {len(derived_metrics)} derived metrics for document {document_id}."
            )
            
        except ExtractionProcessingException as e:
            logger.error(f"Extraction failed for {document_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in extraction pipeline: {e}")
            raise
