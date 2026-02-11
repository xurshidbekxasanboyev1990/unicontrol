"""
UniControl - Mobile Leader Routes
=================================
Leader mobile app endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Schedule
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user, require_leader
from app.config import today_tashkent

router = APIRouter()


class QuickAttendanceRequest(BaseModel):
    """Quick attendance marking request."""
    student_id: int
    status: str  # present, absent, late, excused


class BulkAttendanceRequest(BaseModel):
    """Bulk attendance marking request."""
    attendance_date: date
    records: list[dict]  # [{"student_id": 1, "status": "present"}, ...]


@router.get("/dashboard")
async def get_leader_mobile_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get leader dashboard for mobile.
    """
    # Get leader's group
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    today = today_tashkent()
    
    # Get students count
    students_result = await db.execute(
        select(func.count(Student.id)).where(
            Student.group_id == group.id,
            Student.is_active == True
        )
    )
    students_count = students_result.scalar() or 0
    
    # Today's attendance
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('marked'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.ABSENT, int)).label('absent')
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date == today
        )
    )
    today_stats = today_attendance.first()
    
    # Today's classes
    from app.models.schedule import WeekDay
    weekday = WeekDay(today.isoweekday())
    classes_count = await db.execute(
        select(func.count(Schedule.id)).where(
            Schedule.group_id == group.id,
            Schedule.day_of_week == weekday,
            Schedule.is_active == True
        )
    )
    
    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "code": group.code
        },
        "students_count": students_count,
        "today_attendance": {
            "marked": today_stats.marked or 0,
            "not_marked": students_count - (today_stats.marked or 0),
            "present": today_stats.present or 0,
            "absent": today_stats.absent or 0
        },
        "today_classes": classes_count.scalar() or 0
    }


@router.get("/students")
async def get_group_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get students list for mobile.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    students = await db.execute(
        select(Student).where(
            Student.group_id == group.id,
            Student.is_active == True
        ).order_by(Student.full_name)
    )
    
    return [
        {
            "id": s.id,
            "full_name": s.full_name,
            "hemis_id": s.hemis_id,
            "phone": s.phone
        }
        for s in students.scalars().all()
    ]


@router.get("/attendance/today")
async def get_today_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get today's attendance status for all students.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    today = today_tashkent()
    
    # Get all students with attendance
    students = await db.execute(
        select(Student).where(
            Student.group_id == group.id,
            Student.is_active == True
        ).order_by(Student.full_name)
    )
    
    students_list = students.scalars().all()
    student_ids = [s.id for s in students_list]
    
    # Get today's attendance
    attendance = await db.execute(
        select(Attendance).where(
            Attendance.student_id.in_(student_ids),
            Attendance.date == today
        )
    )
    attendance_map = {a.student_id: a for a in attendance.scalars().all()}
    
    return {
        "date": str(today),
        "students": [
            {
                "id": s.id,
                "full_name": s.full_name,
                "status": attendance_map[s.id].status.value if s.id in attendance_map else None,
                "notes": attendance_map[s.id].notes if s.id in attendance_map else None
            }
            for s in students_list
        ]
    }


@router.post("/attendance/quick")
async def mark_quick_attendance(
    request: QuickAttendanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Quick mark single student attendance.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("No group assigned")
    
    # Verify student is in group
    student = await db.execute(
        select(Student).where(
            Student.id == request.student_id,
            Student.group_id == group.id
        )
    )
    if not student.scalar_one_or_none():
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Student not found in your group")
    
    today = today_tashkent()
    status = AttendanceStatus(request.status)
    
    # Check if already marked
    existing = await db.execute(
        select(Attendance).where(
            Attendance.student_id == request.student_id,
            Attendance.date == today
        )
    )
    attendance = existing.scalar_one_or_none()
    
    if attendance:
        attendance.status = status
        attendance.marked_by = current_user.id
    else:
        attendance = Attendance(
            student_id=request.student_id,
            date=today,
            status=status,
            marked_by=current_user.id
        )
        db.add(attendance)
    
    await db.commit()
    
    return {"message": "Attendance marked", "status": status.value}


@router.post("/attendance/bulk")
async def mark_bulk_attendance(
    request: BulkAttendanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Bulk mark attendance for mobile.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("No group assigned")
    
    marked = 0
    errors = []
    
    for record in request.records:
        try:
            student_id = record["student_id"]
            status = AttendanceStatus(record["status"])
            
            # Check existing
            existing = await db.execute(
                select(Attendance).where(
                    Attendance.student_id == student_id,
                    Attendance.date == request.attendance_date
                )
            )
            attendance = existing.scalar_one_or_none()
            
            if attendance:
                attendance.status = status
                attendance.marked_by = current_user.id
            else:
                attendance = Attendance(
                    student_id=student_id,
                    date=request.attendance_date,
                    status=status,
                    marked_by=current_user.id
                )
                db.add(attendance)
            
            marked += 1
        except Exception as e:
            errors.append(f"Student {record.get('student_id')}: {str(e)}")
    
    await db.commit()
    
    return {
        "marked": marked,
        "errors": errors
    }


@router.get("/schedule/today")
async def get_leader_today_schedule(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get today's schedule for leader.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    from app.models.schedule import WeekDay
    today = today_tashkent()
    weekday = WeekDay(today.isoweekday())
    
    schedules = await db.execute(
        select(Schedule).where(
            Schedule.group_id == group.id,
            Schedule.day_of_week == weekday,
            Schedule.is_active == True
        ).order_by(Schedule.start_time)
    )
    
    return {
        "date": str(today),
        "group": group.name,
        "classes": [
            {
                "id": s.id,
                "subject": s.subject_name,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "room": s.room,
                "teacher": s.teacher_name,
                "is_cancelled": s.is_cancelled
            }
            for s in schedules.scalars().all()
        ]
    }


@router.get("/stats/week")
async def get_week_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get weekly attendance stats for mobile.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    from datetime import timedelta
    today = today_tashkent()
    week_start = today - timedelta(days=today.weekday())
    
    # Get daily stats for the week
    daily_stats = await db.execute(
        select(
            Attendance.date,
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.ABSENT, int)).label('absent')
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date >= week_start
        ).group_by(Attendance.date).order_by(Attendance.date)
    )
    
    return {
        "week_start": str(week_start),
        "daily_stats": [
            {
                "date": str(row.date),
                "total": row.total,
                "present": row.present or 0,
                "absent": row.absent or 0,
                "rate": round(((row.present or 0) / (row.total or 1)) * 100, 1)
            }
            for row in daily_stats.fetchall()
        ]
    }


@router.post("/send-notification")
async def send_group_notification(
    title: str = Query(...),
    message: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Send notification to all group members.
    """
    result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("No group assigned")
    
    # Get all students' user IDs
    students = await db.execute(
        select(Student).where(
            Student.group_id == group.id,
            Student.is_active == True
        )
    )
    
    from app.models.notification import NotificationType
    count = 0
    
    for student in students.scalars().all():
        if student.user_id:
            notification = Notification(
                user_id=student.user_id,
                title=title,
                message=message,
                notification_type=NotificationType.INFO
            )
            db.add(notification)
            count += 1
    
    await db.commit()
    
    return {"message": f"Sent {count} notifications"}
