from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.core.security import get_current_user_token
from app.core.config import settings

router = APIRouter(tags=["Authentication & Users"])

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, response: Response):
    token_obj = await AuthService.register_user(user_in)
    response.set_cookie(
        key="access_token",
        value=token_obj.access_token,
        httponly=True,
        secure=False,  # Set to True in production (HTTPS)
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return token_obj.user

@router.post("/auth/login", response_model=UserResponse)
@router.post("/users/login", response_model=UserResponse)
async def login_user(login_in: UserLogin, response: Response):
    token_obj = await AuthService.authenticate_user(login_in.email, login_in.password)
    response.set_cookie(
        key="access_token",
        value=token_obj.access_token,
        httponly=True,
        secure=False,  # Set to True in production (HTTPS)
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return token_obj.user

@router.post("/auth/logout")
@router.post("/users/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@router.get("/auth/me", response_model=UserResponse)
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(token_data: dict = Depends(get_current_user_token)):
    user_id = token_data.get("sub")
    user_resp = await AuthService.get_user_by_id(user_id)
    if not user_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_resp
