import logging
from app.core.db import get_db
from app.agents.document_agent.processor import DocumentProcessor
from app.agents.extraction_agent.processor import ExtractionProcessor
from app.agents.red_flag_agent.processor import RedFlagProcessor

logger = logging.getLogger(__name__)

class PipelineService:
    @staticmethod
    async def run_full_pipeline(document_id: str, grid_fs_id: str, company_name: str):
        """
        Executes the AI agent pipeline in the background.
        """
        db = get_db()
        docs_col = db["documents"]
        
        async def update_status(status: str):
            await docs_col.update_one({"_id": document_id}, {"$set": {"status": status}})
            
        try:
            # 1. Document Agent
            logger.info(f"Pipeline Step 1/3: Document processing for {document_id}")
            await update_status("PROCESSING")
            await DocumentProcessor.process_document(document_id, grid_fs_id)
            
            # 2. Extraction Agent
            logger.info(f"Pipeline Step 2/3: Metrics extraction for {document_id}")
            await update_status("EXTRACTING_METRICS")
            await ExtractionProcessor.process_extraction(document_id, company_name)
            
            # 3. Red Flag Agent
            logger.info(f"Pipeline Step 3/3: Red flag analysis for {document_id}")
            await update_status("ANALYZING_RED_FLAGS")
            await RedFlagProcessor.process_red_flags(document_id, company_name)
            
            # 4. Finish
            logger.info(f"Pipeline completed for {document_id}")
            await update_status("COMPLETED")
            
        except Exception as e:
            logger.error(f"Pipeline failed for {document_id}: {e}")
            await update_status("FAILED")
