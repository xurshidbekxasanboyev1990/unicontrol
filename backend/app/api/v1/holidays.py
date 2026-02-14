"""
UniControl - Holiday/Off-Day API Routes
=========================================
CRUD endpoints for managing holidays and off-days.

Admin/Super admin can create/update/delete holidays.
All authenticated users can read holidays.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel

from app.database import get_db
from app.config import today_tashkent
from app.models.holiday import Holiday, HolidayType
from app.models.user import User
from app.core.dependencies import get_current_active_user, require_admin

router = APIRouter()


# ===== Pydantic schemas =====

class HolidayCreate(BaseModel):
    title: str
    description: Optional[str] = None
    holiday_type: str = "holiday"
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class HolidayUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    holiday_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None


# ===== Helper =====

def _holiday_to_dict(h: Holiday) -> dict:
    return {
        "id": h.id,
        "title": h.title,
        "description": h.description,
        "holiday_type": h.holiday_type,
        "start_date": h.start_date.isoformat(),
        "end_date": h.end_date.isoformat(),
        "is_active": h.is_active,
        "created_by": h.created_by,
        "created_at": h.created_at.isoformat() if h.created_at else None,
    }


# ===== Endpoints =====

@router.get("")
async def list_holidays(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Barcha bayram/dam olish kunlarini olish"""
    query = select(Holiday).order_by(Holiday.start_date.desc())
    if active_only:
        query = query.where(Holiday.is_active == True)
    result = await db.execute(query)
    holidays = result.scalars().all()
    return [_holiday_to_dict(h) for h in holidays]


@router.get("/active")
async def get_active_holidays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Hozirgi va kelgusi faol bayramlarni olish"""
    today = today_tashkent()
    result = await db.execute(
        select(Holiday).where(
            Holiday.is_active == True,
            Holiday.end_date >= today
        ).order_by(Holiday.start_date.asc())
    )
    holidays = result.scalars().all()
    return [_holiday_to_dict(h) for h in holidays]


@router.get("/check")
async def check_date_holiday(
    check_date: Optional[str] = Query(None, description="YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Berilgan sana bayram/dam olish kuniga to'g'ri keladimi tekshirish"""
    if check_date:
        target = date.fromisoformat(check_date)
    else:
        target = today_tashkent()

    result = await db.execute(
        select(Holiday).where(
            Holiday.is_active == True,
            Holiday.start_date <= target,
            Holiday.end_date >= target
        )
    )
    holiday = result.scalar_one_or_none()
    if holiday:
        return {
            "is_holiday": True,
            "holiday": _holiday_to_dict(holiday)
        }
    return {"is_holiday": False, "holiday": None}


@router.post("")
async def create_holiday(
    data: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yangi bayram/dam olish kuni yaratish (admin/super)"""
    try:
        start = date.fromisoformat(data.start_date)
        end = date.fromisoformat(data.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Noto'g'ri sana formati. YYYY-MM-DD kerak.")

    if end < start:
        raise HTTPException(status_code=400, detail="Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak")

    valid_types = [t.value for t in HolidayType]
    if data.holiday_type not in valid_types:
        data.holiday_type = HolidayType.HOLIDAY.value

    holiday = Holiday(
        title=data.title,
        description=data.description,
        holiday_type=data.holiday_type,
        start_date=start,
        end_date=end,
        created_by=current_user.id,
    )
    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)

    logger.info(f"Holiday created: '{data.title}' ({start} - {end}) by user {current_user.id}")
    return _holiday_to_dict(holiday)


@router.put("/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    data: HolidayUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bayram/dam olish kunini tahrirlash (admin/super)"""
    result = await db.execute(select(Holiday).where(Holiday.id == holiday_id))
    holiday = result.scalar_one_or_none()
    if not holiday:
        raise HTTPException(status_code=404, detail="Bayram topilmadi")

    if data.title is not None:
        holiday.title = data.title
    if data.description is not None:
        holiday.description = data.description
    if data.holiday_type is not None:
        holiday.holiday_type = data.holiday_type
    if data.start_date is not None:
        holiday.start_date = date.fromisoformat(data.start_date)
    if data.end_date is not None:
        holiday.end_date = date.fromisoformat(data.end_date)
    if data.is_active is not None:
        holiday.is_active = data.is_active

    if holiday.end_date < holiday.start_date:
        raise HTTPException(status_code=400, detail="Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak")

    await db.commit()
    await db.refresh(holiday)
    return _holiday_to_dict(holiday)


@router.delete("/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bayram/dam olish kunini o'chirish (admin/super)"""
    result = await db.execute(select(Holiday).where(Holiday.id == holiday_id))
    holiday = result.scalar_one_or_none()
    if not holiday:
        raise HTTPException(status_code=404, detail="Bayram topilmadi")

    await db.delete(holiday)
    await db.commit()
    return {"message": f"'{holiday.title}' o'chirildi", "id": holiday_id}
