class ExtractionProcessingException(Exception):
    """Base exception for extraction agent errors."""
    pass

class InvalidExtractionResultError(ExtractionProcessingException):
    pass

class SourceVerificationFailedError(ExtractionProcessingException):
    pass

class DatabasePersistenceError(ExtractionProcessingException):
    pass

class LLMServiceError(ExtractionProcessingException):
    pass
