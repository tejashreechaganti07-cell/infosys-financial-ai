import uuid
import os
import aiofiles
from datetime import datetime, timezone
from typing import List, Optional
from app.core.db import get_db
from app.schemas.document import DocumentResponse, DocumentListResponse
from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentService:
    @staticmethod
    async def upload_document(
        user_id: str,
        workspace_id: str,
        file: UploadFile,
        company_name: str,
        filing_type: str,
        fiscal_year: int
    ) -> DocumentResponse:
        db = get_db()
        ws_col = db["workspaces"]
        docs_col = db["documents"]
        
        ws = await ws_col.find_one({"_id": workspace_id, "user_id": user_id})
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        
        # Save file to uploads directory
        file_filename = f"{doc_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_filename)
        
        content = await file.read()
        file_size = len(content)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
        
        # Estimated chunk count based on file size
        chunks_count = max(10, file_size // 2500)
        
        doc = {
            "_id": doc_id,
            "title": file.filename,
            "company_name": company_name or "Unknown Company",
            "filing_type": filing_type or "Financial Filing",
            "fiscal_year": int(fiscal_year) if fiscal_year else 2024,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "file_path": f"uploads/{file_filename}",
            "file_size": file_size,
            "status": "INDEXED",
            "is_seed": False,
            "chunks_count": chunks_count,
            "uploaded_at": now_str
        }
        
        await docs_col.insert_one(doc)
        
        # Increment document count on workspace
        await ws_col.update_one(
            {"_id": workspace_id},
            {"$inc": {"documents_count": 1}, "$set": {"updated_at": now_str}}
        )
        
        return DocumentResponse(
            id=doc_id,
            title=doc["title"],
            company_name=doc["company_name"],
            filing_type=doc["filing_type"],
            fiscal_year=doc["fiscal_year"],
            workspace_id=doc["workspace_id"],
            user_id=doc["user_id"],
            file_path=doc["file_path"],
            file_size=doc["file_size"],
            status=doc["status"],
            is_seed=doc["is_seed"],
            chunks_count=doc["chunks_count"],
            uploaded_at=doc["uploaded_at"]
        )

    @staticmethod
    async def list_documents(user_id: str, workspace_id: Optional[str] = None) -> DocumentListResponse:
        db = get_db()
        docs_col = db["documents"]
        
        query = {"user_id": user_id}
        if workspace_id:
            query["workspace_id"] = workspace_id
            
        cursor = docs_col.find(query).sort("uploaded_at", -1)
        items = []
        async for doc in cursor:
            items.append(DocumentResponse(
                id=doc["_id"],
                title=doc["title"],
                company_name=doc["company_name"],
                filing_type=doc["filing_type"],
                fiscal_year=doc["fiscal_year"],
                workspace_id=doc["workspace_id"],
                user_id=doc["user_id"],
                file_path=doc["file_path"],
                file_size=doc["file_size"],
                status=doc["status"],
                is_seed=doc.get("is_seed", False),
                chunks_count=doc.get("chunks_count", 0),
                uploaded_at=doc["uploaded_at"]
            ))
        return DocumentListResponse(documents=items, total=len(items))

    @staticmethod
    async def get_document(user_id: str, doc_id: str) -> DocumentResponse:
        db = get_db()
        docs_col = db["documents"]
        
        doc = await docs_col.find_one({"_id": doc_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        return DocumentResponse(
            id=doc["_id"],
            title=doc["title"],
            company_name=doc["company_name"],
            filing_type=doc["filing_type"],
            fiscal_year=doc["fiscal_year"],
            workspace_id=doc["workspace_id"],
            user_id=doc["user_id"],
            file_path=doc["file_path"],
            file_size=doc["file_size"],
            status=doc["status"],
            is_seed=doc.get("is_seed", False),
            chunks_count=doc.get("chunks_count", 0),
            uploaded_at=doc["uploaded_at"]
        )

    @staticmethod
    async def delete_document(user_id: str, doc_id: str) -> bool:
        db = get_db()
        docs_col = db["documents"]
        ws_col = db["workspaces"]
        
        doc = await docs_col.find_one({"_id": doc_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        await docs_col.delete_one({"_id": doc_id})
        
        # Decrement workspace document count
        if doc.get("workspace_id"):
            await ws_col.update_one(
                {"_id": doc["workspace_id"]},
                {"$inc": {"documents_count": -1}}
            )
            
        return True
