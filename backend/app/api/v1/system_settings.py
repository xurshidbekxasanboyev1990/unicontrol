"""
Settings API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_active_user

router = APIRouter()


class SettingsResponse(BaseModel):
    """Settings response model"""
    institution_name: str = "UniControl"
    institution_logo: Optional[str] = None
    institution_address: Optional[str] = None
    institution_phone: Optional[str] = None
    institution_email: Optional[str] = None
    academic_year: str = "2025-2026"
    semester: str = "1"
    attendance_threshold: int = 80
    late_minutes_threshold: int = 15
    working_hours_start: str = "08:00"
    working_hours_end: str = "18:00"
    telegram_bot_enabled: bool = True
    email_notifications_enabled: bool = True
    sms_notifications_enabled: bool = False
    ai_analysis_enabled: bool = True
    language: str = "uz"
    timezone: str = "Asia/Tashkent"
    theme: str = "light"
    extra: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    """Settings update model"""
    institution_name: Optional[str] = None
    institution_logo: Optional[str] = None
    institution_address: Optional[str] = None
    institution_phone: Optional[str] = None
    institution_email: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    attendance_threshold: Optional[int] = None
    late_minutes_threshold: Optional[int] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    telegram_bot_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    ai_analysis_enabled: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


# In-memory settings (production da database da saqlash kerak)
_settings = SettingsResponse()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_active_user)
):
    """Tizim sozlamalarini olish"""
    return _settings


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Tizim sozlamalarini yangilash (faqat super_admin)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin sozlamalarni o'zgartira oladi")
    
    global _settings
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(_settings, field, value)
    
    return _settings
