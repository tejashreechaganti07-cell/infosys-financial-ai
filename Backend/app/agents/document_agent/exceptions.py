class DocumentProcessingException(Exception):
    """Base exception for document processing errors."""
    pass

class InvalidFileTypeError(DocumentProcessingException):
    pass

class FileTooLargeError(DocumentProcessingException):
    pass

class CorruptedPDFError(DocumentProcessingException):
    pass

class EmptyDocumentError(DocumentProcessingException):
    pass

class FileNotFoundInGridFSError(DocumentProcessingException):
    pass

class TextExtractionFailedError(DocumentProcessingException):
    pass

class OCRFailedError(DocumentProcessingException):
    pass

class TableExtractionFailedError(DocumentProcessingException):
    pass

class ChunkingFailedError(DocumentProcessingException):
    pass

class EmbeddingFailedError(DocumentProcessingException):
    pass

class DatabasePersistenceError(DocumentProcessingException):
    pass
