"""
UniControl - Attendance Routes
==============================
Attendance tracking endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.attendance_service import AttendanceService
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBatch,
    AttendanceStats,
    DailyAttendanceSummary,
    StudentAttendanceSummary,
)
from app.models.attendance import AttendanceStatus
from app.core.dependencies import get_current_active_user, require_leader
from app.models.user import User

router = APIRouter()


@router.get("")
async def list_attendance(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    group_id: Optional[int] = None,
    student_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[AttendanceStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List attendance records with filters.
    """
    service = AttendanceService(db)
    attendances, total = await service.list_attendance(
        page=page,
        page_size=page_size,
        group_id=group_id,
        student_id=student_id,
        date_from=date_from,
        date_to=date_to,
        status=status
    )
    
    return {
        "items": [AttendanceResponse.model_validate(a) for a in attendances],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create or update attendance record.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    attendance = await service.create(attendance_data, current_user.id)
    return AttendanceResponse.model_validate(attendance)


@router.post("/batch", response_model=list)
async def create_batch_attendance(
    batch_data: AttendanceBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create attendance records in batch.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    attendances = await service.batch_create(batch_data, current_user.id)
    return [AttendanceResponse.model_validate(a) for a in attendances]


@router.get("/daily-summary", response_model=DailyAttendanceSummary)
async def get_daily_summary(
    target_date: date = Query(default=None),
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance summary for a day.
    """
    if target_date is None:
        target_date = date.today()
    
    service = AttendanceService(db)
    return await service.get_daily_summary(target_date, group_id)


@router.get("/student/{student_id}/stats", response_model=AttendanceStats)
async def get_student_stats(
    student_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance statistics for a student.
    """
    service = AttendanceService(db)
    return await service.get_student_stats(student_id, date_from, date_to)


@router.get("/student/{student_id}", response_model=list)
async def get_student_attendance(
    student_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance records for a student.
    """
    service = AttendanceService(db)
    attendances = await service.get_student_attendance(student_id, date_from, date_to)
    return [AttendanceResponse.model_validate(a) for a in attendances]


@router.get("/group/{group_id}/summary", response_model=list)
async def get_group_summary(
    group_id: int,
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get attendance summary for all students in a group.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    return await service.get_group_attendance_summary(group_id, date_from, date_to)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance record by ID.
    """
    service = AttendanceService(db)
    attendance = await service.get_by_id(attendance_id)
    if not attendance:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Attendance record not found")
    return AttendanceResponse.model_validate(attendance)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Update attendance record.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    attendance = await service.update(attendance_id, attendance_data)
    return AttendanceResponse.model_validate(attendance)


@router.delete("/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Delete attendance record.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    await service.delete(attendance_id)
    return {"message": "Attendance record deleted"}


@router.post("/mark-absent", response_model=dict)
async def mark_absent_for_date(
    target_date: date,
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Mark all students without attendance as absent for a date.
    
    Requires leader role.
    """
    service = AttendanceService(db)
    count = await service.mark_absent_for_date(target_date, group_id, current_user.id)
    return {"message": f"Marked {count} students as absent"}
