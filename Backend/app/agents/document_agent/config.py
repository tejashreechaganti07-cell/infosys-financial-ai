import os

# Limits
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Embeddings
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en"

# Database Collections
COLLECTION_CHUNKS = "parsed_chunks"
COLLECTION_EMBEDDINGS = "embeddings"
COLLECTION_TABLES = "tables"
COLLECTION_DOCUMENTS = "documents"
