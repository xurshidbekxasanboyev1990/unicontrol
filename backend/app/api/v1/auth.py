"""
UniControl - Authentication Routes
==================================
Login, logout, token refresh endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserLogin,
    Token,
    UserResponse,
    UserCreate,
    PasswordUpdate,
    RefreshToken,
)
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns access and refresh tokens.
    """
    service = AuthService(db)
    return await service.login(credentials)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    return await service.refresh_tokens(token_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me/password")
async def change_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.
    """
    service = AuthService(db)
    await service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout():
    """
    Logout current user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint is for API completeness.
    """
    return {"message": "Logged out successfully"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Note: In production, this should be restricted or require admin approval.
    """
    service = AuthService(db)
    user = await service.register(user_data)
    return UserResponse.model_validate(user)
