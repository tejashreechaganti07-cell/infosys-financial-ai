import logging
from .schemas import DocumentProcessingResult
from .validators import DocumentValidator
from .storage import StorageManager
from .pdf_parser import PDFParser
from .ocr import OCRProcessor
from .table_extractor import TableExtractor
from .chunker import HybridChunker
from .embeddings import EmbeddingGenerator
from .exceptions import DocumentProcessingException

logger = logging.getLogger(__name__)

class DocumentProcessor:
    @staticmethod
    async def process_document(document_id: str, grid_fs_id: str) -> DocumentProcessingResult:
        logger.info(f"Starting processing for document: {document_id}")
        await StorageManager.update_document_status(document_id, {"processing_status": "processing"})
        
        try:
            # 1. Fetch file bytes from GridFS
            file_bytes = await StorageManager.get_pdf_bytes_from_gridfs(grid_fs_id)
            
            # 2. Validation
            await StorageManager.update_document_status(document_id, {"processing_status": "validating"})
            DocumentValidator.validate_file_size(len(file_bytes))
            DocumentValidator.validate_pdf_content(file_bytes)
            
            # 3. PDF Parsing
            await StorageManager.update_document_status(document_id, {"processing_status": "extracting_text"})
            pages, requires_ocr = PDFParser.extract_text(document_id, file_bytes)
            
            # 4. OCR (if needed)
            if requires_ocr:
                await StorageManager.update_document_status(document_id, {"processing_status": "performing_ocr"})
                pages = OCRProcessor.process_empty_pages(document_id, file_bytes, pages)
                
            # 5. Table Extraction
            await StorageManager.update_document_status(document_id, {"processing_status": "extracting_tables"})
            tables = TableExtractor.extract_tables(document_id, file_bytes)
            await StorageManager.save_tables(tables)
            
            # 6. Chunking
            await StorageManager.update_document_status(document_id, {"processing_status": "chunking"})
            chunks = HybridChunker.create_chunks(document_id, pages)
            await StorageManager.save_chunks(chunks)
            
            # 7. Embeddings
            await StorageManager.update_document_status(document_id, {"processing_status": "generating_embeddings"})
            embeddings_created = 0
            try:
                await EmbeddingGenerator.generate_and_save_embeddings(document_id, chunks)
                embeddings_created = len(chunks)
            except Exception as e:
                logger.error(f"Embedding failed, but proceeding: {e}")
                # Depending on decision, we either retry or mark as warning.
                # User said: "If embedding fails retry the entire process as it will extract data that will be required for another agent"
                # If we want to retry the entire process, we raise the exception to let the caller handle it.
                raise
                
            # 8. Complete
            await StorageManager.update_document_status(document_id, {"processing_status": "completed"})
            logger.info(f"Successfully completed processing for document: {document_id}")
            
            return DocumentProcessingResult(
                document_id=document_id,
                status="completed",
                page_count=len(pages),
                chunks_created=len(chunks),
                tables_detected=len(tables),
                embeddings_created=embeddings_created
            )
            
        except DocumentProcessingException as e:
            logger.error(f"DocumentProcessingException for {document_id}: {e}")
            await StorageManager.update_document_status(document_id, {"processing_status": "failed", "error": str(e)})
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {document_id}: {e}")
            await StorageManager.update_document_status(document_id, {"processing_status": "failed", "error": str(e)})
            raise
