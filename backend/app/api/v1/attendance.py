"""
UniControl - Attendance Routes
==============================
Attendance tracking endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date, datetime, timedelta
from app.config import now_tashkent, today_tashkent
from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.services.attendance_service import AttendanceService
from app.services.telegram_notifier import send_attendance_to_telegram, send_batch_attendance_summary_to_telegram
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBatch,
    AttendanceStats,
    DailyAttendanceSummary,
    StudentAttendanceSummary,
)
from app.models.attendance import Attendance as AttendanceModel, AttendanceStatus
from app.models.student import Student
from app.models.group import Group
from app.core.dependencies import get_current_active_user, require_leader
from app.models.user import User, UserRole

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
    
    is_superadmin = current_user.role == UserRole.SUPERADMIN
    
    return {
        "items": [AttendanceResponse.from_attendance(a, is_superadmin) for a in attendances],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance_data: AttendanceCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create or update attendance record.
    
    Requires leader role.
    Sends real-time notification to Telegram only for NEW records (not upserts).
    """
    service = AttendanceService(db)
    attendance, is_new = await service.create(attendance_data, current_user.id)
    
    # Only send Telegram notification for NEW records, not upsert updates
    if is_new:
        try:
            # Load student with group
            student_result = await db.execute(
                select(Student).options(selectinload(Student.group)).where(Student.id == attendance.student_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student and student.group:
                background_tasks.add_task(
                    send_attendance_to_telegram,
                    db,
                    attendance,
                    student,
                    student.group
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Telegram notification error: {e}")
    
    return AttendanceResponse.model_validate(attendance)


@router.post("/batch", response_model=list)
async def create_batch_attendance(
    batch_data: AttendanceBatch,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create attendance records in batch.
    
    Requires leader role.
    Sends ONE summary notification to Telegram (not per-student).
    Only notifies if there are genuinely new records (not re-saves of existing).
    """
    service = AttendanceService(db)
    attendances, new_count = await service.batch_create(batch_data, current_user.id)
    
    # Send ONE summary notification (not 50 individual messages)
    # Only send if there are new records (skip if all are re-saves/upserts)
    if new_count > 0 and attendances:
        try:
            first = attendances[0]
            student_result = await db.execute(
                select(Student).options(selectinload(Student.group)).where(Student.id == first.student_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student and student.group:
                # Load all students for name display in summary
                for att in attendances:
                    s_result = await db.execute(
                        select(Student).where(Student.id == att.student_id)
                    )
                    s = s_result.scalar_one_or_none()
                    if s:
                        att._student_name = getattr(s, 'full_name', None) or getattr(s, 'name', "Noma'lum")
                    else:
                        att._student_name = "Noma'lum"
                
                background_tasks.add_task(
                    send_batch_attendance_summary_to_telegram,
                    db,
                    attendances,
                    student.group,
                    batch_data.lesson_number,
                    batch_data.subject,
                    False,  # is_update=False (new batch)
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Telegram batch notification error: {e}")
    
    return [AttendanceResponse.model_validate(a) for a in attendances]


@router.get("/daily-summary", response_model=DailyAttendanceSummary)
async def get_daily_summary(
    target_date: date = Query(default=None),
    group_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance summary for a day.
    group_id can be either numeric ID or group name string.
    """
    if target_date is None:
        target_date = today_tashkent()
    
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


@router.get("/export/printable")
async def export_attendance_printable(
    group_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Export attendance to print-ready Excel.
    Leaders: auto-resolves own group. Dean+ can pass group_id.
    """
    from fastapi.responses import StreamingResponse
    from app.services.excel_service import ExcelService

    # Leader auto-resolve group
    if not group_id and current_user.role == UserRole.LEADER:
        grp_result = await db.execute(
            select(Group).where(Group.leader_id == current_user.id)
        )
        grp = grp_result.scalars().first()
        if grp:
            group_id = grp.id

    if not date_from:
        date_from = today_tashkent()
    if not date_to:
        date_to = date_from

    service = ExcelService(db)
    file_data = await service.export_attendance_printable(
        group_id=group_id,
        date_from=date_from,
        date_to=date_to,
        status_filter=status_filter,
    )

    fname_parts = ["davomat"]
    if group_id:
        fname_parts.append(f"guruh_{group_id}")
    fname_parts.append(date_from.strftime("%d_%m_%Y"))
    if date_to != date_from:
        fname_parts.append(date_to.strftime("%d_%m_%Y"))
    filename = "_".join(fname_parts) + ".xlsx"

    return StreamingResponse(
        file_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Update attendance record.
    
    Requires leader role.
    Admin/leader cannot edit after 24 hours. Superadmin can always edit.
    Does NOT re-send Telegram notification to avoid duplicates.
    """
    service = AttendanceService(db)
    attendance = await service.get_by_id(attendance_id)
    if not attendance:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Attendance record not found")
    
    # 24-hour edit lock: only superadmin can edit after 24 hours
    if current_user.role != UserRole.SUPERADMIN:
        now = now_tashkent()
        created = attendance.created_at
        # Ensure both are tz-aware for comparison
        if created and (not hasattr(created, 'tzinfo') or created.tzinfo is None):
            from app.config import TASHKENT_TZ
            created = TASHKENT_TZ.localize(created)
        time_since_creation = now - created
        if time_since_creation > timedelta(hours=24):
            from fastapi import HTTPException as HTTPErr
            raise HTTPErr(
                status_code=403,
                detail="Davomatni tahrirlash vaqti tugagan (24 soatdan oshgan). Faqat super admin o'zgartira oladi."
            )
    
    # Remember old status to check if changed
    old_status = attendance.status
    
    attendance = await service.update(attendance_id, attendance_data)
    
    # Only send notification if status actually changed (not just a re-save)
    new_status = attendance.status
    if old_status != new_status:
        try:
            student_result = await db.execute(
                select(Student).options(selectinload(Student.group)).where(Student.id == attendance.student_id)
            )
            student = student_result.scalar_one_or_none()
            
            if student and student.group:
                background_tasks.add_task(
                    send_attendance_to_telegram,
                    db,
                    attendance,
                    student,
                    student.group
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Telegram update notification error: {e}")
    
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