"""
Statistics API Routes
======================
Provides statistics for dashboard and reports.

Endpoints:
- GET /statistics/dashboard - General dashboard stats
- GET /statistics/attendance - Attendance statistics
- GET /statistics/contracts - Contract statistics (placeholder)
"""

import time
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Student, Group, Attendance
from app.models.attendance import AttendanceStatus
from app.models.user import UserRole
from app.core.dependencies import get_current_active_user, require_admin
from app.config import today_tashkent


router = APIRouter()

# Simple in-memory cache for dashboard stats
_dashboard_cache = {"data": None, "timestamp": 0, "ttl": 30}  # 30 sekund


@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get general dashboard statistics.
    Uses in-memory cache (30s TTL) to reduce DB load.
    """
    now = time.time()
    if _dashboard_cache["data"] and (now - _dashboard_cache["timestamp"] < _dashboard_cache["ttl"]):
        return _dashboard_cache["data"]

    # Total students
    students_result = await db.execute(select(func.count(Student.id)))
    total_students = students_result.scalar() or 0
    
    # Total groups
    groups_result = await db.execute(select(func.count(Group.id)))
    total_groups = groups_result.scalar() or 0
    
    # Total users
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0
    
    # Active students (where is_active = True)
    active_students_result = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    active_students = active_students_result.scalar() or 0
    
    # Today's attendance count
    today = today_tashkent()
    today_attendance_result = await db.execute(
        select(func.count(Attendance.id)).where(Attendance.date == today)
    )
    today_attendance = today_attendance_result.scalar() or 0
    
    result = {
        "total_students": total_students,
        "total_groups": total_groups,
        "total_users": total_users,
        "active_students": active_students,
        "today_attendance": today_attendance
    }

    # Cache saqlash
    _dashboard_cache["data"] = result
    _dashboard_cache["timestamp"] = now

    return result


@router.get("/attendance")
async def get_attendance_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance statistics.
    """
    # Default date range - last 30 days
    if not date_from:
        date_from = today_tashkent() - timedelta(days=30)
    if not date_to:
        date_to = today_tashkent()
    
    # Base date filter conditions
    base_conditions = [
        Attendance.date >= date_from,
        Attendance.date <= date_to
    ]
    
    # If group_id specified, get student IDs in that group
    student_ids = None
    if group_id:
        students_query = select(Student.id).where(Student.group_id == group_id)
        students_result = await db.execute(students_query)
        student_ids = [s for s in students_result.scalars()]
        if not student_ids:
            return {
                "total_records": 0,
                "present_count": 0,
                "absent_count": 0,
                "late_count": 0,
                "attendance_rate": 0.0,
                "date_from": str(date_from),
                "date_to": str(date_to)
            }
    
    def _add_group_filter(q):
        """Apply group filter if student_ids are set."""
        if student_ids is not None:
            return q.where(Attendance.student_id.in_(student_ids))
        return q
    
    # Total records
    query = select(func.count(Attendance.id)).where(*base_conditions)
    query = _add_group_filter(query)
    total_result = await db.execute(query)
    total_records = total_result.scalar() or 0
    
    # Present count
    present_query = select(func.count(Attendance.id)).where(
        *base_conditions,
        Attendance.status == AttendanceStatus.PRESENT
    )
    present_query = _add_group_filter(present_query)
    present_result = await db.execute(present_query)
    present_count = present_result.scalar() or 0
    
    # Absent count
    absent_query = select(func.count(Attendance.id)).where(
        *base_conditions,
        Attendance.status == AttendanceStatus.ABSENT
    )
    absent_query = _add_group_filter(absent_query)
    absent_result = await db.execute(absent_query)
    absent_count = absent_result.scalar() or 0
    
    # Late count
    late_query = select(func.count(Attendance.id)).where(
        *base_conditions,
        Attendance.status == AttendanceStatus.LATE
    )
    late_query = _add_group_filter(late_query)
    late_result = await db.execute(late_query)
    late_count = late_result.scalar() or 0
    
    # Attendance rate
    attendance_rate = 0.0
    if total_records > 0:
        attendance_rate = round((present_count + late_count) / total_records * 100, 1)
    
    return {
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "attendance_rate": attendance_rate,
        "date_from": str(date_from),
        "date_to": str(date_to)
    }


@router.get("/contracts")
async def get_contract_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get contract statistics (placeholder).
    """
    # Placeholder - can be extended later
    return {
        "total_contracts": 0,
        "active_contracts": 0,
        "expired_contracts": 0,
        "pending_payment": 0,
        "total_amount": 0,
        "paid_amount": 0
    }


@router.get("/users")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user statistics by role.
    """
    result = {}
    
    for role in UserRole:
        count_result = await db.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        result[role.value] = count_result.scalar() or 0
    
    total_result = await db.execute(select(func.count(User.id)))
    result["total"] = total_result.scalar() or 0
    
    return result
