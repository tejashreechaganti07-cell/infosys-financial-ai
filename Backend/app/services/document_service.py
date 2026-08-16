import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.db import get_db, get_grid_fs
from app.schemas.document import DocumentResponse, DocumentListResponse
from fastapi import UploadFile, HTTPException, status, BackgroundTasks
from app.services.pipeline_service import PipelineService

class DocumentService:
    @staticmethod
    async def upload_document(
        user_id: str,
        workspace_id: str,
        file: UploadFile,
        company_name: str,
        filing_type: str,
        fiscal_year: int,
        background_tasks: BackgroundTasks
    ) -> DocumentResponse:
        db = get_db()
        grid_fs = get_grid_fs()
        ws_col = db["workspaces"]
        docs_col = db["documents"]
        
        ws = await ws_col.find_one({"_id": workspace_id, "user_id": user_id})
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        
        content = await file.read()
        file_size = len(content)
        file_filename = f"{doc_id}_{file.filename}"
        
        # Upload to GridFS
        grid_in = grid_fs.open_upload_stream(
            file_filename,
            metadata={"content_type": file.content_type, "workspace_id": workspace_id, "user_id": user_id}
        )
        await grid_in.write(content)
        await grid_in.close()
        grid_file_id = str(grid_in._id)
        
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
            "file_path": f"gridfs://{grid_file_id}",
            "grid_fs_id": grid_file_id,
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
        
        # Trigger the AI agent pipeline in the background
        # Since BackgroundTasks runs in the same event loop, we can just pass the coroutine
        import asyncio
        background_tasks.add_task(
            PipelineService.run_full_pipeline,
            document_id=doc_id,
            grid_fs_id=grid_file_id,
            company_name=doc["company_name"]
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
        grid_fs = get_grid_fs()
        docs_col = db["documents"]
        ws_col = db["workspaces"]
        
        doc = await docs_col.find_one({"_id": doc_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        await docs_col.delete_one({"_id": doc_id})
        
        # Delete from GridFS if present
        if doc.get("grid_fs_id"):
            from bson.objectid import ObjectId
            try:
                await grid_fs.delete(ObjectId(doc["grid_fs_id"]))
            except Exception as e:
                import logging
                logging.getLogger("uvicorn").error(f"Failed to delete GridFS file: {e}")
        
        # Decrement workspace document count
        if doc.get("workspace_id"):
            await ws_col.update_one(
                {"_id": doc["workspace_id"]},
                {"$inc": {"documents_count": -1}}
            )
            
        return True
