import io
import logging
from typing import List, Tuple
from pypdf import PdfReader
from .schemas import DocumentPage

logger = logging.getLogger(__name__)

class PDFParser:
    @staticmethod
    def extract_text(document_id: str, file_bytes: bytes) -> Tuple[List[DocumentPage], bool]:
        """
        Extracts text from the PDF.
        Returns a tuple of (pages, requires_ocr)
        """
        pages = []
        requires_ocr = False
        empty_pages_count = 0
        
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                
                if text:
                    text = text.strip()
                else:
                    text = ""
                    
                if not text:
                    empty_pages_count += 1
                
                pages.append(DocumentPage(
                    document_id=document_id,
                    page_number=page_number,
                    text=text,
                    ocr_used=False
                ))
            
            # Simple heuristic: if more than 50% of the pages are empty, we likely need OCR
            if total_pages > 0 and (empty_pages_count / total_pages) > 0.5:
                requires_ocr = True
                
            return pages, requires_ocr
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {document_id}: {e}")
            from .exceptions import TextExtractionFailedError
            raise TextExtractionFailedError(f"PDF parsing failed: {e}")
