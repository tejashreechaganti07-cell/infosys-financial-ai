import logging
from typing import List
from app.core.db import get_db
from .schemas import ValidatedMetric, DerivedMetric
from .config import COLLECTION_EXTRACTED_METRICS, COLLECTION_DERIVED_METRICS
from .exceptions import DatabasePersistenceError

logger = logging.getLogger(__name__)

class ExtractionStorage:
    @staticmethod
    async def save_extracted_metrics(metrics: List[ValidatedMetric]):
        if not metrics:
            return
            
        db = get_db()
        col = db[COLLECTION_EXTRACTED_METRICS]
        
        # Conflict detection: Store both and flag
        # We group by (document_id, metric_name, fiscal_year)
        grouped = {}
        for m in metrics:
            if m.fiscal_year is None:
                continue
            key = (m.document_id, m.metric_name, m.fiscal_year)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)
            
        for key, group in grouped.items():
            if len(group) > 1:
                # Conflict detected!
                for m in group:
                    m.status = "conflicting"
                    logger.warning(f"Conflict detected for {m.metric_name} in year {m.fiscal_year}")
                    
        docs = [m.model_dump() for m in metrics]
        try:
            await col.insert_many(docs)
            logger.info(f"Saved {len(docs)} extracted metrics to DB.")
        except Exception as e:
            logger.error(f"Failed to save extracted metrics: {e}")
            raise DatabasePersistenceError(f"DB Error: {e}")

    @staticmethod
    async def save_derived_metrics(metrics: List[DerivedMetric]):
        if not metrics:
            return
            
        db = get_db()
        col = db[COLLECTION_DERIVED_METRICS]
        
        docs = [m.model_dump() for m in metrics]
        try:
            await col.insert_many(docs)
            logger.info(f"Saved {len(docs)} derived metrics to DB.")
        except Exception as e:
            logger.error(f"Failed to save derived metrics: {e}")
            raise DatabasePersistenceError(f"DB Error: {e}")
