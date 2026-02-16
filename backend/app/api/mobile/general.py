"""
UniControl - Mobile General Routes
=================================
Common mobile endpoints without /student or /leader prefix to support older mobile clients.

These act as lightweight proxies to existing logic (student/leader) and provide
group/notifications helpers used by the mobile app.
"""

from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Schedule, WeekDay
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user, require_leader
from app.config import today_tashkent

router = APIRouter()


@router.get("/schedule")
async def mobile_schedule(
    group_id: Optional[int] = Query(None),
    day: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return schedule for current user (student) or for group if provided."""
    # If group_id provided and user is leader/admin, return group week
    if group_id:
        schedules = await db.execute(
            select(Schedule).where(Schedule.group_id == group_id, Schedule.is_active == True).order_by(Schedule.day_of_week, Schedule.start_time)
        )
        items = []
        for s in schedules.scalars().all():
            items.append({
                "id": s.id,
                "subject": s.subject,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "room": s.room,
                "teacher": s.teacher_name,
                "day": s.day_of_week.name,
                "is_cancelled": s.is_cancelled,
            })
        return {"schedule": items}

    # Otherwise if user is student -> return their week schedule
    student_res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    schedules = await db.execute(
        select(Schedule).where(Schedule.group_id == student.group_id, Schedule.is_active == True).order_by(Schedule.day_of_week, Schedule.start_time)
    )

    week_schedule = {day.name: [] for day in WeekDay}
    for s in schedules.scalars().all():
        week_schedule[s.day_of_week.name].append({
            "id": s.id,
            "subject": s.subject,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "room": s.room,
            "teacher": s.teacher_name,
            "is_cancelled": s.is_cancelled,
        })

    # If day query provided, normalize and return single day
    if day:
        dn = day.strip().lower()
        try:
            wd = WeekDay(dn)
            return {wd.name: week_schedule.get(wd.name, [])}
        except Exception:
            return {"error": "Invalid day"}

    return week_schedule


@router.get("/attendance")
async def mobile_attendance(
    student_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return attendance records for current student or specified student (leader)."""
    # If requesting another student, require leader role
    if student_id and student_id != getattr(current_user, 'id', None):
        # basic check: ensure current_user is leader of that student's group
        student_row = await db.execute(select(Student).where(Student.id == student_id))
        target = student_row.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="Student not found")
        from app.models.group import Group
        grp = await db.execute(select(Group).where(Group.leader_id == current_user.id))
        if not grp.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not allowed")

    # Default to current student's records
    if not student_id:
        row = await db.execute(select(Student).where(Student.user_id == current_user.id))
        student = row.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        student_id = student.id

    start_date = today_tashkent() - timedelta(days=days)
    attendance = await db.execute(
        select(Attendance).where(Attendance.student_id == student_id, Attendance.date >= start_date).order_by(Attendance.date.desc())
    )
    records = attendance.scalars().all()
    return {
        "records": [
            {"date": str(a.date), "status": a.status.value, "notes": a.notes} for a in records
        ]
    }


@router.get("/groups")
async def mobile_groups(db: AsyncSession = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    offset = (page - 1) * page_size
    res = await db.execute(select(Group).offset(offset).limit(page_size))
    groups = res.scalars().all()
    return {"items": [{"id": g.id, "name": g.name} for g in groups], "page": page, "page_size": page_size}


@router.get("/groups/{group_id}/students")
async def mobile_group_students(group_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Student).where(Student.group_id == group_id, Student.is_active == True))
    students = res.scalars().all()
    return {"items": [{"id": s.id, "full_name": s.full_name, "hemis_id": s.student_id} for s in students]}


@router.get("/notifications/unread-count")
async def mobile_unread_count(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    res = await db.execute(select(func.count(Notification.id)).where(Notification.user_id == current_user.id, Notification.is_read == False))
    count = res.scalar() or 0
    return {"count": count}
