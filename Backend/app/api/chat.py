from fastapi import APIRouter, Depends
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatHistoryResponse
from app.services.chat_service import ChatService
from app.core.security import get_current_user_token

router = APIRouter(prefix="/chat", tags=["Conversational Research Interface"])

@router.post("/query", response_model=ChatQueryResponse)
async def query_chat(query_in: ChatQueryRequest, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await ChatService.query_chat(user_id, query_in)

@router.get("/history/{workspace_id}", response_model=ChatHistoryResponse)
async def get_chat_history(workspace_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await ChatService.get_history(user_id, workspace_id)
