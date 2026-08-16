from typing import Union
import io
from .config import MAX_FILE_SIZE
from .exceptions import InvalidFileTypeError, FileTooLargeError, CorruptedPDFError, EmptyDocumentError

class DocumentValidator:
    @staticmethod
    def validate_file_size(file_size: int):
        if file_size > MAX_FILE_SIZE:
            raise FileTooLargeError(f"File size {file_size} exceeds maximum limit of {MAX_FILE_SIZE} bytes.")

    @staticmethod
    def validate_pdf_content(file_bytes: bytes):
        if not file_bytes:
            raise EmptyDocumentError("The document is empty.")
            
        # Basic signature check
        if not file_bytes.startswith(b'%PDF-'):
            raise InvalidFileTypeError("The file does not appear to be a valid PDF.")
            
        # We can also attempt a quick parse with PyPDF to check for corruption
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            if len(reader.pages) == 0:
                raise EmptyDocumentError("The PDF contains no pages.")
        except Exception as e:
            if isinstance(e, EmptyDocumentError):
                raise
            raise CorruptedPDFError(f"The PDF is corrupted or unreadable: {str(e)}")
