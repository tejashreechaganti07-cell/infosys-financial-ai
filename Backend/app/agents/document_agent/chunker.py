import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .schemas import DocumentPage, DocumentChunk
from .section_detector import SectionDetector
from .config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class HybridChunker:
    @staticmethod
    def create_chunks(document_id: str, pages: List[DocumentPage]) -> List[DocumentChunk]:
        """
        Creates semantic chunks that respect page boundaries and detect sections.
        """
        all_chunks = []
        chunk_idx = 1
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        for page in pages:
            if not page.text.strip():
                continue
                
            # Split page text into chunks
            text_chunks = splitter.split_text(page.text)
            
            for text_chunk in text_chunks:
                section = SectionDetector.detect_section(text_chunk)
                
                # We calculate token_count roughly as word count * 1.3
                token_count = int(len(text_chunk.split()) * 1.3)
                
                chunk = DocumentChunk(
                    chunk_id=f"chunk_{document_id}_{chunk_idx}",
                    document_id=document_id,
                    chunk_index=chunk_idx,
                    page_start=page.page_number,
                    page_end=page.page_number,
                    section_type=section,
                    text=text_chunk,
                    token_count=token_count
                )
                
                all_chunks.append(chunk)
                chunk_idx += 1
                
        logger.info(f"Created {len(all_chunks)} chunks for document {document_id}")
        return all_chunks
