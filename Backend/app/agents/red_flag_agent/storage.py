import logging
from typing import List
from app.core.db import get_db
from app.agents.red_flag_agent.schemas import RedFlag
from app.agents.red_flag_agent.config import COLLECTION_RED_FLAGS
from app.agents.red_flag_agent.exceptions import DatabasePersistenceError

logger = logging.getLogger(__name__)

class RedFlagStorage:
    @staticmethod
    async def save_flags(flags: List[RedFlag]):
        if not flags:
            logger.info("No red flags to save.")
            return
            
        db = get_db()
        col = db[COLLECTION_RED_FLAGS]
        
        docs = [f.model_dump() for f in flags]
        try:
            await col.insert_many(docs)
            logger.info(f"Saved {len(docs)} red flags to DB.")
        except Exception as e:
            logger.error(f"Failed to save red flags: {e}")
            raise DatabasePersistenceError(f"DB Error: {e}")
