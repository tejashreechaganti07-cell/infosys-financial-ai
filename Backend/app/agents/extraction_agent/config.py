# Extraction Agent Configuration

# MongoDB Collections
COLLECTION_CHUNKS = "parsed_chunks"
COLLECTION_EMBEDDINGS = "embeddings"
COLLECTION_DOCUMENTS = "documents"
COLLECTION_EXTRACTED_METRICS = "extracted_metrics"
COLLECTION_DERIVED_METRICS = "derived_metrics"

# LLM Configuration
LLM_MODEL = "gpt-4o"

# Retrieval Configuration
MAX_CHUNKS_TO_RETRIEVE = 10
VECTOR_SEARCH_LIMIT = 5
VECTOR_SEARCH_INDEX = "vector_index" # Assumes this is setup in Atlas

# Required Metrics MVP List
REQUIRED_METRICS = [
    "Revenue",
    "Gross Profit",
    "Operating Income",
    "Net Income",
    "EPS",
    "Total Assets",
    "Total Liabilities",
    "Total Equity",
    "Cash",
    "Total Debt",
    "Operating Cash Flow",
    "Capital Expenditure",
    "Free Cash Flow"
]
