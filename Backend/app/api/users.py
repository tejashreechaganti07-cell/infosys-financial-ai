from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.core.security import get_current_user_token

router = APIRouter(tags=["Authentication & Users"])

@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@router.post("/users/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    return await AuthService.register_user(user_in)

@router.post("/auth/login", response_model=Token)
@router.post("/users/login", response_model=Token)
async def login_user(login_in: UserLogin):
    return await AuthService.authenticate_user(login_in.email, login_in.password)

@router.get("/auth/me", response_model=UserResponse)
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    user_resp = await AuthService.get_user_by_id(user_id)
    if not user_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_resp
