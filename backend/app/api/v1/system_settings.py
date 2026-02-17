"""
Settings API Routes
==================
Tizim sozlamalari - PostgreSQL DB da saqlanadi (singleton, id=1)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database import get_db
from app.models.user import User, UserRole
from app.models.system_settings import SystemSettings
from app.core.dependencies import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()


class SettingsResponse(BaseModel):
    """Settings response model"""
    institution_name: str = "UniControl"
    institution_logo: Optional[str] = None
    institution_address: Optional[str] = None
    institution_phone: Optional[str] = None
    institution_email: Optional[str] = None
    academic_year: str = "2025-2026"
    semester: str = "2"
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


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """Get singleton settings row (id=1), create if not exists."""
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SystemSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        logger.info("SystemSettings row created with defaults")
    return settings


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Tizim sozlamalarini olish"""
    settings = await get_or_create_settings(db)
    return settings.to_dict()


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Tizim sozlamalarini yangilash (faqat super_admin va admin)"""
    if current_user.role not in (UserRole.SUPERADMIN, UserRole.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Faqat super admin yoki admin sozlamalarni o'zgartira oladi"
        )
    
    settings = await get_or_create_settings(db)
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    logger.info(f"Settings updated by {current_user.username}: {list(update_data.keys())}")
    
    return settings.to_dict()
