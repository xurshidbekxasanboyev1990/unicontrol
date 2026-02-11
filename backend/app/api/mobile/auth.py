"""
UniControl - Mobile Auth Routes
===============================
Mobile authentication endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


class MobileLoginRequest(BaseModel):
    """Mobile login request."""
    username: str
    password: str
    device_token: str | None = None
    device_type: str = "android"  # android, ios


class MobileLoginResponse(BaseModel):
    """Mobile login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


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
    result = await service.authenticate(
        username=request.username,
        password=request.password,
        device_token=request.device_token,
        device_type=request.device_type
    )
    
    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
        "user": {
            "id": result["user"].id,
            "username": result["user"].username,
            "email": result["user"].email,
            "full_name": result["user"].full_name,
            "role": result["user"].role.value,
            "avatar": result["user"].avatar
        }
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token.
    """
    service = AuthService(db)
    result = await service.refresh_token(refresh_token)
    
    return {
        "access_token": result["access_token"],
        "token_type": "bearer"
    }


@router.post("/logout")
async def mobile_logout(
    device_token: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mobile logout - removes device token.
    """
    service = AuthService(db)
    await service.logout(current_user.id, device_token)
    
    return {"message": "Logged out successfully"}


@router.post("/register-device")
async def register_device(
    request: DeviceRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Register device for push notifications.
    """
    service = AuthService(db)
    await service.register_device(
        user_id=current_user.id,
        device_token=request.device_token,
        device_type=request.device_type
    )
    
    return {"message": "Device registered"}


@router.get("/me")
async def get_current_user_mobile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user info for mobile.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "avatar": current_user.avatar,
        "is_active": current_user.is_active
    }
