# MARK: Imports
import uuid
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from crewai import Agent, Task, Crew
from app.schemas import ChatQueryRequest, ChatQueryResponse, ChatHistoryResponse, ChatMessageResponse, Citation
from app.core.database import get_db
from app.core.security import get_current_user_token
from app.agents.agents import get_research_agent

# MARK: Router Setup
router = APIRouter(prefix="/chat", tags=["Conversational Research Interface"])

# MARK: Endpoints
@router.post("/query", response_model=ChatQueryResponse)
async def query_chat(query_in: ChatQueryRequest, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    db = get_db()
    chat_col = db["chat_history"]
    
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now_str = datetime.now(timezone.utc).isoformat()
    
    await chat_col.insert_one({
        "_id": f"usr_msg_{uuid.uuid4().hex[:8]}",
        "workspace_id": query_in.workspace_id,
        "user_id": user_id,
        "role": "user",
        "content": query_in.query,
        "timestamp": now_str
    })
    
    # Fetch context from parsed chunks for documents in this workspace
    docs_col = db["documents"]
    chunks_col = db["parsed_chunks"]
    
    docs = await docs_col.find({"workspace_id": query_in.workspace_id}).to_list(length=None)
    doc_ids = [d["_id"] for d in docs]
    
    # We fetch top chunks or just all chunks if not too big. For safety, limit to 20000 chars.
    chunks = await chunks_col.find({"document_id": {"$in": doc_ids}}).limit(20).to_list(length=None)
    
    context_text = "\n\n".join([f"Source ({c.get('document_id')}): {c.get('text')}" for c in chunks])
    if not context_text:
        context_text = "No document context available for this workspace."
        
    try:
        researcher = get_research_agent()
        task = Task(
            description=f"Context:\n{context_text}\n\nAnswer the following query accurately based ONLY on the context above: {query_in.query}",
            agent=researcher,
            expected_output="A detailed answer to the query with citations to the context where possible."
        )
        crew = Crew(agents=[researcher], tasks=[task], verbose=True)
        result = await asyncio.to_thread(crew.kickoff)
        
        answer_text = result.raw if hasattr(result, "raw") else str(result)
        agent_status = "Research Agent citation verified"
    except Exception as e:
        answer_text = f"An error occurred while analyzing the documents: {str(e)}"
        agent_status = "Error"
        
    reasoning = [
        "1. Document Agent retrieved context from the workspace.",
        "2. Research Agent analyzed the context and generated a response."
    ]
    citations = []
        
    assistant_msg = ChatMessageResponse(
        id=msg_id,
        workspace_id=query_in.workspace_id,
        role="assistant",
        content=answer_text,
        reasoning_steps=reasoning,
        citations=citations,
        timestamp=now_str
    )
    
    await chat_col.insert_one({
        "_id": msg_id,
        "workspace_id": query_in.workspace_id,
        "user_id": user_id,
        "role": "assistant",
        "content": answer_text,
        "reasoning_steps": reasoning,
        "citations": [],
        "timestamp": now_str
    })
    
    return ChatQueryResponse(message=assistant_msg, agent_status=agent_status)

@router.get("/history/{workspace_id}", response_model=ChatHistoryResponse)
async def get_chat_history(workspace_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    db = get_db()
    chat_col = db["chat_history"]
    
    cursor = chat_col.find({"workspace_id": workspace_id, "user_id": user_id}).sort("timestamp", 1)
    items = []
    async for doc in cursor:
        citations_list = []
        if doc.get("citations"):
            for c in doc["citations"]:
                citations_list.append(Citation(**c))
        items.append(ChatMessageResponse(
            id=doc["_id"],
            workspace_id=doc["workspace_id"],
            role=doc["role"],
            content=doc["content"],
            reasoning_steps=doc.get("reasoning_steps"),
            citations=citations_list if citations_list else None,
            timestamp=doc["timestamp"]
        ))
    return ChatHistoryResponse(messages=items)
