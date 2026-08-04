import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.db import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceListResponse
from fastapi import HTTPException, status

class WorkspaceService:
    @staticmethod
    async def create_workspace(user_id: str, ws_in: WorkspaceCreate) -> WorkspaceResponse:
        db = get_db()
        ws_col = db["workspaces"]
        
        ws_id = f"ws_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        
        doc = {
            "_id": ws_id,
            "name": ws_in.name,
            "description": ws_in.description or "",
            "user_id": user_id,
            "created_at": now_str,
            "updated_at": now_str,
            "documents_count": 0
        }
        await ws_col.insert_one(doc)
        
        return WorkspaceResponse(
            id=ws_id,
            name=doc["name"],
            description=doc["description"],
            user_id=doc["user_id"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            documents_count=0
        )

    @staticmethod
    async def list_workspaces(user_id: str) -> WorkspaceListResponse:
        db = get_db()
        ws_col = db["workspaces"]
        
        cursor = ws_col.find({"user_id": user_id}).sort("updated_at", -1)
        items = []
        async for doc in cursor:
            items.append(WorkspaceResponse(
                id=doc["_id"],
                name=doc["name"],
                description=doc.get("description", ""),
                user_id=doc["user_id"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                documents_count=doc.get("documents_count", 0)
            ))
        return WorkspaceListResponse(workspaces=items, total=len(items))

    @staticmethod
    async def get_workspace(user_id: str, ws_id: str) -> WorkspaceResponse:
        db = get_db()
        ws_col = db["workspaces"]
        
        doc = await ws_col.find_one({"_id": ws_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
            
        return WorkspaceResponse(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description", ""),
            user_id=doc["user_id"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            documents_count=doc.get("documents_count", 0)
        )

    @staticmethod
    async def update_workspace(user_id: str, ws_id: str, ws_in: WorkspaceUpdate) -> WorkspaceResponse:
        db = get_db()
        ws_col = db["workspaces"]
        
        doc = await ws_col.find_one({"_id": ws_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        
        update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if ws_in.name is not None:
            update_fields["name"] = ws_in.name
        if ws_in.description is not None:
            update_fields["description"] = ws_in.description
            
        await ws_col.update_one({"_id": ws_id}, {"$set": update_fields})
        doc.update(update_fields)
        
        return WorkspaceResponse(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description", ""),
            user_id=doc["user_id"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            documents_count=doc.get("documents_count", 0)
        )

    @staticmethod
    async def delete_workspace(user_id: str, ws_id: str) -> bool:
        db = get_db()
        ws_col = db["workspaces"]
        docs_col = db["documents"]
        
        result = await ws_col.delete_one({"_id": ws_id, "user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
            
        await docs_col.delete_many({"workspace_id": ws_id})
        return True
