"""
UniControl - Schedule Routes
============================
Schedule management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleListResponse,
    WeekSchedule,
    DaySchedule,
    CancelSchedule,
)
from app.models.schedule import WeekDay
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.config import today_tashkent

router = APIRouter()


@router.get("", response_model=ScheduleListResponse)
async def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    group_id: Optional[int] = None,
    day_of_week: Optional[WeekDay] = None,
    is_active: Optional[bool] = True,
    semester: Optional[int] = None,
    academic_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List schedules with filters.
    """
    service = ScheduleService(db)
    schedules, total = await service.list_schedules(
        page=page,
        page_size=page_size,
        group_id=group_id,
        day_of_week=day_of_week,
        is_active=is_active,
        semester=semester,
        academic_year=academic_year
    )
    
    return ScheduleListResponse(
        items=[ScheduleResponse.model_validate(s) for s in schedules],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new schedule.
    
    Requires admin role.
    """
    service = ScheduleService(db)
    schedule = await service.create(schedule_data)
    return ScheduleResponse.model_validate(schedule)


@router.get("/today", response_model=list)
async def get_today_schedules(
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get today's schedules.
    """
    service = ScheduleService(db)
    schedules = await service.get_today_schedules(group_id)
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get("/group/{group_id}/week", response_model=WeekSchedule)
async def get_group_week_schedule(
    group_id: int,
    semester: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get weekly schedule for a group.
    """
    service = ScheduleService(db)
    return await service.get_group_week_schedule(group_id, semester)


@router.get("/group/{group_id}/day", response_model=DaySchedule)
async def get_group_day_schedule(
    group_id: int,
    target_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get schedule for a specific day.
    """
    if target_date is None:
        target_date = today_tashkent()
    
    service = ScheduleService(db)
    return await service.get_day_schedule(group_id, target_date)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get schedule by ID.
    """
    service = ScheduleService(db)
    schedule = await service.get_by_id(schedule_id)
    if not schedule:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Schedule not found")
    return ScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update schedule.
    
    Requires admin role.
    """
    service = ScheduleService(db)
    schedule = await service.update(schedule_id, schedule_data)
    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete schedule.
    
    Requires admin role.
    """
    service = ScheduleService(db)
    await service.delete(schedule_id)
    return {"message": "Schedule deleted"}


@router.post("/{schedule_id}/cancel", response_model=ScheduleResponse)
async def cancel_schedule(
    schedule_id: int,
    data: CancelSchedule,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Cancel a schedule.
    
    Requires admin role.
    """
    service = ScheduleService(db)
    schedule = await service.cancel_schedule(schedule_id, data.cancellation_reason)
    return ScheduleResponse.model_validate(schedule)


@router.post("/{schedule_id}/restore", response_model=ScheduleResponse)
async def restore_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Restore a cancelled schedule.
    
    Requires admin role.
    """
    service = ScheduleService(db)
    schedule = await service.restore_schedule(schedule_id)
    return ScheduleResponse.model_validate(schedule)
