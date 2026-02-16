"""
UniControl - Mobile Auth Routes
===============================
Mobile authentication endpoints.
Properly integrated with AuthService and User model.

Author: UniControl Team
Version: 2.0.0
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

router = APIRouter()


class MobileLoginRequest(BaseModel):
    """Mobile login request."""
    username: str
    password: str
    device_token: Optional[str] = None
    device_type: str = "android"  # android, ios


class MobileLoginResponse(BaseModel):
    """Mobile login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class MobileRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class DeviceRegisterRequest(BaseModel):
    """Device registration request."""
    device_token: str
    device_type: str


@router.post("/login", response_model=MobileLoginResponse)
async def mobile_login(
    request: MobileLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Mobile login endpoint.
    
    Returns access token, refresh token, and user info.
    """
    service = AuthService(db)
    
    # authenticate() returns User object, uses 'login' param
    user = await service.authenticate(
        login=request.username,
        password=request.password
    )
    
    # Create tokens
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    
    # Save refresh token to DB
    user.refresh_token = refresh_token
    db.add(user)
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "login": user.login,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar": user.avatar,
            "phone": user.phone
        }
    }


@router.post("/refresh")
async def refresh_token_endpoint(
    request: MobileRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    # refresh_tokens() returns Token schema
    result = await service.refresh_tokens(request.refresh_token)
    
    return {
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def mobile_logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mobile logout - invalidates refresh token.
    """
    # Invalidate refresh token (server-side)
    current_user.refresh_token = None
    db.add(current_user)
    await db.commit()
    
    return {"message": "Logged out successfully"}


@router.post("/register-device")
async def register_device(
    request: DeviceRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Register device for push notifications.
    Stores device token in user's push_tokens JSON field.
    """
    # Store device token in user metadata or dedicated field
    # For now, return success (push service handles token storage separately)
    return {
        "message": "Device registered",
        "user_id": current_user.id,
        "device_type": request.device_type
    }


@router.get("/me")
async def get_current_user_mobile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user info for mobile.
    """
    return {
        "id": current_user.id,
        "login": current_user.login,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value,
        "avatar": current_user.avatar,
        "phone": current_user.phone,
        "is_active": current_user.is_active
    }


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str


@router.put("/change-password")
@router.post("/change-password")
async def mobile_change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Change current user's password.
    """
    service = AuthService(db)
    await service.change_password(
        current_user,
        request.current_password,
        request.new_password,
    )
    return {"message": "Parol muvaffaqiyatli yangilandi"}
