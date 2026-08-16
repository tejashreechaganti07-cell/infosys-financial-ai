import logging
from typing import List, Dict, Any
from app.core.db import get_db
from .config import COLLECTION_EMBEDDINGS, COLLECTION_CHUNKS, VECTOR_SEARCH_INDEX, MAX_CHUNKS_TO_RETRIEVE
from app.agents.document_agent.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class HybridRetriever:
    # Map metrics to expected sections
    METRIC_SECTION_MAP = {
        "Revenue": ["income_statement", "md_and_a"],
        "Gross Profit": ["income_statement", "md_and_a"],
        "Operating Income": ["income_statement", "md_and_a"],
        "Net Income": ["income_statement", "cash_flow_statement"],
        "EPS": ["income_statement", "financial_notes"],
        "Total Assets": ["balance_sheet"],
        "Total Liabilities": ["balance_sheet"],
        "Total Equity": ["balance_sheet"],
        "Cash": ["balance_sheet", "cash_flow_statement"],
        "Total Debt": ["balance_sheet", "financial_notes"],
        "Operating Cash Flow": ["cash_flow_statement"],
        "Capital Expenditure": ["cash_flow_statement"],
        "Free Cash Flow": ["cash_flow_statement", "md_and_a"]
    }

    @classmethod
    async def retrieve_chunks(cls, document_id: str, metric_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves relevant chunks using Atlas Vector Search filtered by section.
        """
        db = get_db()
        col = db[COLLECTION_EMBEDDINGS]
        
        # 1. Generate embedding for the metric query
        try:
            model = EmbeddingGenerator.get_model()
            query_vector = model.encode([metric_name], convert_to_numpy=True).tolist()[0]
        except Exception as e:
            logger.error(f"Failed to generate query vector for {metric_name}: {e}")
            return []
            
        # 2. Determine target sections
        target_sections = cls.METRIC_SECTION_MAP.get(metric_name, ["unknown"])
        
        # 3. Perform Vector Search (Hybrid)
        # Note: In a real MongoDB Atlas environment, this requires the vector_index to be created.
        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_SEARCH_INDEX,
                    "path": "vector",
                    "queryVector": query_vector,
                    "numCandidates": 50,
                    "limit": MAX_CHUNKS_TO_RETRIEVE,
                    "filter": {
                        "document_id": document_id,
                        # Filtering by section requires the section_type to be stored in the embeddings collection
                        # For now, we fetch chunks and filter post-search or assume chunks have the section.
                        # Wait, our embeddings collection only has document_id, chunk_id. 
                        # We must fetch the actual chunk data from parsed_chunks collection via $lookup
                    }
                }
            },
            {
                "$lookup": {
                    "from": COLLECTION_CHUNKS,
                    "localField": "chunk_id",
                    "foreignField": "chunk_id",
                    "as": "chunk_data"
                }
            },
            {
                "$unwind": "$chunk_data"
            },
            {
                "$match": {
                    "chunk_data.section_type": {"$in": target_sections + ["unknown"]}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "chunk_id": "$chunk_data.chunk_id",
                    "text": "$chunk_data.text",
                    "page_number": "$chunk_data.page_start",
                    "section_type": "$chunk_data.section_type"
                }
            }
        ]
        
        try:
            cursor = col.aggregate(pipeline)
            results = await cursor.to_list(length=MAX_CHUNKS_TO_RETRIEVE)
            logger.info(f"Retrieved {len(results)} chunks for metric {metric_name}")
            return results
        except Exception as e:
            logger.error(f"Vector search failed for {metric_name}: {e}")
            # Fallback to simple text search or fetching all chunks if Atlas Vector Search is not configured locally
            return await cls._fallback_retrieval(document_id, metric_name)

    @classmethod
    async def _fallback_retrieval(cls, document_id: str, metric_name: str) -> List[Dict[str, Any]]:
        """Fallback to fetch chunks based on section if vector search fails."""
        db = get_db()
        col = db[COLLECTION_CHUNKS]
        target_sections = cls.METRIC_SECTION_MAP.get(metric_name, ["unknown"])
        
        cursor = col.find({
            "document_id": document_id,
            "section_type": {"$in": target_sections + ["unknown"]}
        }).limit(MAX_CHUNKS_TO_RETRIEVE)
        
        results = await cursor.to_list(length=MAX_CHUNKS_TO_RETRIEVE)
        
        formatted = []
        for r in results:
            formatted.append({
                "chunk_id": r["chunk_id"],
                "text": r["text"],
                "page_number": r["page_start"],
                "section_type": r["section_type"]
            })
            
        return formatted
