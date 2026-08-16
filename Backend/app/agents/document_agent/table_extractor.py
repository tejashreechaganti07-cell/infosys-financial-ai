import io
import uuid
import logging
from typing import List
from .schemas import DocumentTable
from .exceptions import TableExtractionFailedError

logger = logging.getLogger(__name__)

class TableExtractor:
    @staticmethod
    def extract_tables(document_id: str, file_bytes: bytes) -> List[DocumentTable]:
        tables_list = []
        try:
            import pdfplumber
            
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    extracted_tables = page.extract_tables()
                    
                    for idx, table in enumerate(extracted_tables):
                        # A table is a list of lists.
                        if not table or len(table) < 2:
                            continue
                            
                        # Naive extraction: assume first row is headers
                        headers = [str(col).strip() if col else "" for col in table[0]]
                        
                        rows = []
                        for row in table[1:]:
                            if not any(row):  # Skip empty rows
                                continue
                            
                            row_label = str(row[0]).strip() if row[0] else ""
                            values = [str(col).strip() if col else "" for col in row[1:]]
                            
                            rows.append({
                                "label": row_label,
                                "values": values
                            })
                            
                        tables_list.append(DocumentTable(
                            table_id=f"table_{document_id}_{page_num}_{idx}",
                            document_id=document_id,
                            page_number=page_num,
                            title=f"Table on page {page_num}",
                            headers=headers,
                            rows=rows
                        ))
                        
            logger.info(f"Extracted {len(tables_list)} tables from document {document_id}")
            return tables_list
            
        except ImportError:
            logger.error("pdfplumber is not installed. Cannot extract tables.")
            raise TableExtractionFailedError("pdfplumber is missing.")
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            raise TableExtractionFailedError(f"Failed to extract tables: {e}")
