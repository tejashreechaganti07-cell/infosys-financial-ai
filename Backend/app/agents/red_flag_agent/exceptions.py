class RedFlagProcessingException(Exception):
    """Base exception for red flag agent errors."""
    pass

class RuleExecutionError(RedFlagProcessingException):
    pass

class QualitativeAnalysisError(RedFlagProcessingException):
    pass

class DatabasePersistenceError(RedFlagProcessingException):
    pass
