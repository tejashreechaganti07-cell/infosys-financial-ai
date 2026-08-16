import logging
from typing import List, Dict, Any
from bson.objectid import ObjectId
from app.core.db import get_db, get_grid_fs
from .config import COLLECTION_CHUNKS, COLLECTION_EMBEDDINGS, COLLECTION_TABLES, COLLECTION_DOCUMENTS
from .schemas import DocumentChunk, DocumentTable
from .exceptions import DatabasePersistenceError

logger = logging.getLogger(__name__)

class StorageManager:
    @staticmethod
    async def get_pdf_bytes_from_gridfs(grid_fs_id: str) -> bytes:
        from bson.objectid import ObjectId
        grid_fs = get_grid_fs()
        try:
            grid_out = await grid_fs.open_download_stream(ObjectId(grid_fs_id))
            file_bytes = await grid_out.read()
            return file_bytes
        except Exception as e:
            from .exceptions import FileNotFoundInGridFSError
            logger.error(f"Failed to fetch file from GridFS with ID {grid_fs_id}: {e}")
            raise FileNotFoundInGridFSError(f"Could not retrieve file bytes from GridFS: {e}")

    @staticmethod
    async def save_chunks(chunks: List[DocumentChunk]):
        db = get_db()
        col = db[COLLECTION_CHUNKS]
        if not chunks:
            return
            
        docs = [chunk.model_dump() for chunk in chunks]
        try:
            await col.insert_many(docs)
            logger.info(f"Successfully saved {len(chunks)} chunks to {COLLECTION_CHUNKS}.")
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
            raise DatabasePersistenceError(f"Database error while saving chunks: {e}")

    @staticmethod
    async def save_tables(tables: List[DocumentTable]):
        db = get_db()
        col = db[COLLECTION_TABLES]
        if not tables:
            return
            
        docs = [table.model_dump() for table in tables]
        try:
            await col.insert_many(docs)
            logger.info(f"Successfully saved {len(tables)} tables to {COLLECTION_TABLES}.")
        except Exception as e:
            logger.error(f"Failed to save tables: {e}")
            raise DatabasePersistenceError(f"Database error while saving tables: {e}")

    @staticmethod
    async def update_document_status(document_id: str, update_fields: Dict[str, Any]):
        db = get_db()
        col = db[COLLECTION_DOCUMENTS]
        try:
            await col.update_one(
                {"_id": document_id},
                {"$set": update_fields}
            )
        except Exception as e:
            logger.error(f"Failed to update document status for {document_id}: {e}")
            raise DatabasePersistenceError(f"Database error while updating document status: {e}")
