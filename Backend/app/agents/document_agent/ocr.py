import io
import logging
from typing import List
from .schemas import DocumentPage
from .exceptions import OCRFailedError

logger = logging.getLogger(__name__)

class OCRProcessor:
    @staticmethod
    def process_empty_pages(document_id: str, file_bytes: bytes, pages: List[DocumentPage]) -> List[DocumentPage]:
        """
        Attempts to run OCR on pages that have empty text.
        """
        empty_pages = [p for p in pages if not p.text.strip()]
        
        if not empty_pages:
            return pages
            
        try:
            import pdf2image
            import pytesseract
            
            logger.info(f"Running OCR on {len(empty_pages)} empty pages for document {document_id}")
            
            # Convert PDF to images (only the required pages if possible, or all and map them)
            # For simplicity, we convert all pages here and match by index. 
            # In a production environment with huge PDFs, we should only convert specific pages.
            images = pdf2image.convert_from_bytes(file_bytes)
            
            for page in empty_pages:
                page_idx = page.page_number - 1
                if page_idx < len(images):
                    image = images[page_idx]
                    text = pytesseract.image_to_string(image)
                    page.text = text.strip()
                    page.ocr_used = True
                    
        except ImportError:
            logger.warning("pdf2image or pytesseract not installed. Skipping OCR.")
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            # We don't raise OCRFailedError here to allow best-effort extraction to continue
            
        return pages
