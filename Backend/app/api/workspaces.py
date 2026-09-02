from fastapi import APIRouter, Depends, status
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceListResponse
from app.services.workspace_service import WorkspaceService
from app.core.security import get_current_user_token

router = APIRouter(prefix="/workspaces", tags=["Research Workspaces"])

@router.get("", response_model=WorkspaceListResponse)
@router.get("/", response_model=WorkspaceListResponse)
async def get_workspaces(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await WorkspaceService.list_workspaces(user_id)

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(ws_in: WorkspaceCreate, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await WorkspaceService.create_workspace(user_id, ws_in)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await WorkspaceService.get_workspace(user_id, workspace_id)

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(workspace_id: str, ws_in: WorkspaceUpdate, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    return await WorkspaceService.update_workspace(user_id, workspace_id, ws_in)

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(workspace_id: str, token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    await WorkspaceService.delete_workspace(user_id, workspace_id)
    return None
