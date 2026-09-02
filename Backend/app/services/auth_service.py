import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.core.db import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.schemas.user import UserCreate, UserResponse, Token


class AuthService:

    @staticmethod
    async def register_user(user_in: UserCreate) -> Token:
        db = get_db()
        users_col = db["users"]

        existing = await users_col.find_one(
            {"email": user_in.email.lower()}
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already registered",
            )

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        doc = {
            "_id": user_id,
            "email": user_in.email.lower(),
            "full_name": user_in.full_name,
            "hashed_password": hash_password(user_in.password),
            "role": user_in.role or "Financial Analyst",
            "created_at": now_str,
        }

        await users_col.insert_one(doc)

        user_resp = UserResponse(
            id=user_id,
            email=doc["email"],
            full_name=doc["full_name"],
            role=doc["role"],
            created_at=doc["created_at"],
        )

        token_str = create_access_token(subject=user_id)

        return Token(
            access_token=token_str,
            token_type="bearer",
            user=user_resp,
        )

    @staticmethod
    async def authenticate_user(
        email: str,
        password: str,
    ) -> Token:

        db = get_db()
        users_col = db["users"]

        user_doc = await users_col.find_one(
            {"email": email.lower()}
        )

        if not user_doc or not verify_password(
            password,
            user_doc.get("hashed_password", ""),
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_resp = UserResponse(
            id=user_doc["_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            role=user_doc.get(
                "role",
                "Financial Analyst",
            ),
            created_at=user_doc.get(
                "created_at",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        token_str = create_access_token(
            subject=user_doc["_id"]
        )

        return Token(
            access_token=token_str,
            token_type="bearer",
            user=user_resp,
        )

    @staticmethod
    async def get_user_by_id(
        user_id: str,
    ) -> Optional[UserResponse]:

        db = get_db()
        users_col = db["users"]

        user_doc = await users_col.find_one(
            {"_id": user_id}
        )

        if not user_doc:
            return None

        return UserResponse(
            id=user_doc["_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            role=user_doc.get(
                "role",
                "Financial Analyst",
            ),
            created_at=user_doc.get(
                "created_at",
                datetime.now(timezone.utc).isoformat(),
            ),
        )