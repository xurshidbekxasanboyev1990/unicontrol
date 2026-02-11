"""
UniControl - Mobile Student Routes
==================================
Student mobile app endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Schedule
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.config import today_tashkent

router = APIRouter()


@router.get("/profile")
async def get_student_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student profile for mobile.
    """
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    return {
        "id": student.id,
        "full_name": student.full_name,
        "hemis_id": student.hemis_id,
        "email": student.email,
        "phone": student.phone,
        "group_id": student.group_id,
        "contract_number": student.contract_number,
        "avatar": current_user.avatar
    }


@router.get("/dashboard")
async def get_mobile_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get compact dashboard for mobile.
    """
    # Get student
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    today = today_tashkent()
    
    # Today's attendance
    today_attendance = await db.execute(
        select(Attendance).where(
            Attendance.student_id == student.id,
            Attendance.date == today
        )
    )
    today_record = today_attendance.scalar_one_or_none()
    
    # This month's stats
    month_start = today.replace(day=1)
    month_stats = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).where(
            Attendance.student_id == student.id,
            Attendance.date >= month_start
        )
    )
    stats = month_stats.first()
    
    # Today's schedule count
    from app.models.schedule import WeekDay
    weekday = WeekDay(today.isoweekday())
    schedule_count = await db.execute(
        select(func.count(Schedule.id)).where(
            Schedule.group_id == student.group_id,
            Schedule.day_of_week == weekday,
            Schedule.is_active == True
        )
    )
    
    # Unread notifications
    unread = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    
    return {
        "student_name": student.full_name,
        "today_status": today_record.status.value if today_record else "not_marked",
        "attendance_rate": round(((stats.present or 0) / (stats.total or 1)) * 100, 1),
        "today_classes": schedule_count.scalar() or 0,
        "unread_notifications": unread.scalar() or 0
    }


@router.get("/attendance")
async def get_attendance_history(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance history for mobile.
    """
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    from datetime import timedelta
    start_date = today_tashkent() - timedelta(days=days)
    
    attendance = await db.execute(
        select(Attendance).where(
            Attendance.student_id == student.id,
            Attendance.date >= start_date
        ).order_by(Attendance.date.desc())
    )
    
    records = attendance.scalars().all()
    
    return {
        "records": [
            {
                "date": str(a.date),
                "status": a.status.value,
                "notes": a.notes
            }
            for a in records
        ],
        "stats": {
            "total": len(records),
            "present": sum(1 for a in records if a.status == AttendanceStatus.PRESENT),
            "absent": sum(1 for a in records if a.status == AttendanceStatus.ABSENT),
            "late": sum(1 for a in records if a.status == AttendanceStatus.LATE)
        }
    }


@router.get("/schedule/today")
async def get_today_schedule(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get today's schedule for mobile.
    """
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    from app.models.schedule import WeekDay
    today = today_tashkent()
    weekday = WeekDay(today.isoweekday())
    
    schedules = await db.execute(
        select(Schedule).where(
            Schedule.group_id == student.group_id,
            Schedule.day_of_week == weekday,
            Schedule.is_active == True,
            Schedule.is_cancelled == False
        ).order_by(Schedule.start_time)
    )
    
    return {
        "date": str(today),
        "day": weekday.name,
        "classes": [
            {
                "id": s.id,
                "subject": s.subject_name,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "room": s.room,
                "teacher": s.teacher_name
            }
            for s in schedules.scalars().all()
        ]
    }


@router.get("/schedule/week")
async def get_week_schedule(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get weekly schedule for mobile.
    """
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    from app.models.schedule import WeekDay
    
    schedules = await db.execute(
        select(Schedule).where(
            Schedule.group_id == student.group_id,
            Schedule.is_active == True
        ).order_by(Schedule.day_of_week, Schedule.start_time)
    )
    
    # Group by day
    week_schedule = {day.name: [] for day in WeekDay}
    
    for s in schedules.scalars().all():
        week_schedule[s.day_of_week.name].append({
            "id": s.id,
            "subject": s.subject_name,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "room": s.room,
            "teacher": s.teacher_name,
            "is_cancelled": s.is_cancelled
        })
    
    return week_schedule


@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get notifications for mobile.
    """
    offset = (page - 1) * page_size
    
    # Get notifications
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id
        ).order_by(
            Notification.is_read,
            Notification.created_at.desc()
        ).offset(offset).limit(page_size)
    )
    notifications = result.scalars().all()
    
    # Get total count
    total_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id
        )
    )
    total = total_result.scalar() or 0
    
    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type.value if n.notification_type else "info",
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark notification as read.
    """
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Notification not found")
    
    notification.is_read = True
    await db.commit()
    
    return {"message": "Marked as read"}
