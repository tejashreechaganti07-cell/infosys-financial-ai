import logging
from typing import List
from .schemas import DocumentChunk
from .config import EMBEDDING_MODEL_NAME, COLLECTION_EMBEDDINGS
from .exceptions import EmbeddingFailedError
from app.core.db import get_db

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
                cls._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            except ImportError:
                logger.error("sentence-transformers not installed.")
                raise EmbeddingFailedError("sentence-transformers missing")
        return cls._model

    @classmethod
    async def generate_and_save_embeddings(cls, document_id: str, chunks: List[DocumentChunk]):
        if not chunks:
            return
            
        try:
            model = cls.get_model()
            texts = [chunk.text for chunk in chunks]
            
            # Generate embeddings
            embeddings = model.encode(texts, convert_to_numpy=True).tolist()
            
            db = get_db()
            col = db[COLLECTION_EMBEDDINGS]
            
            docs = []
            for chunk, vector in zip(chunks, embeddings):
                docs.append({
                    "embedding_id": f"emb_{chunk.chunk_id}",
                    "chunk_id": chunk.chunk_id,
                    "document_id": document_id,
                    "vector": vector,
                    "model_name": EMBEDDING_MODEL_NAME
                })
                
            await col.insert_many(docs)
            logger.info(f"Generated and saved {len(docs)} embeddings for document {document_id}")
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingFailedError(f"Failed to generate embeddings: {e}")
