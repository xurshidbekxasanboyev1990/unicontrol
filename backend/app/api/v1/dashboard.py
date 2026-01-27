"""
UniControl - Dashboard Routes
=============================
Dashboard data endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.notification import Notification
from app.models.report import Report
from app.core.dependencies import (
    get_current_active_user,
    require_leader,
    require_admin,
    require_superadmin
)

router = APIRouter()


@router.get("/student")
async def get_student_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student dashboard data.
    """
    # Get student info
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        return {"error": "Student profile not found"}
    
    # Get attendance stats
    today = date.today()
    month_start = today.replace(day=1)
    
    attendance_result = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.ABSENT, int)).label('absent'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.LATE, int)).label('late')
        ).where(
            Attendance.student_id == student.id,
            Attendance.date >= month_start
        )
    )
    attendance_stats = attendance_result.first()
    
    # Get unread notifications
    notif_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    unread_notifications = notif_result.scalar() or 0
    
    return {
        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "group_id": student.group_id,
            "hemis_id": student.hemis_id
        },
        "attendance": {
            "total_days": attendance_stats.total or 0,
            "present": attendance_stats.present or 0,
            "absent": attendance_stats.absent or 0,
            "late": attendance_stats.late or 0,
            "attendance_rate": round(
                ((attendance_stats.present or 0) / (attendance_stats.total or 1)) * 100, 1
            )
        },
        "unread_notifications": unread_notifications
    }


@router.get("/leader")
async def get_leader_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get leader dashboard data.
    """
    # Get leader's group
    group_result = await db.execute(
        select(Group).where(Group.leader_id == current_user.id)
    )
    group = group_result.scalar_one_or_none()
    
    if not group:
        return {"error": "No group assigned"}
    
    # Get group students count
    students_result = await db.execute(
        select(func.count(Student.id)).where(
            Student.group_id == group.id,
            Student.is_active == True
        )
    )
    students_count = students_result.scalar() or 0
    
    # Get today's attendance
    today = date.today()
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date == today
        )
    )
    today_stats = today_attendance.first()
    
    # Get this week attendance trend
    week_start = today - timedelta(days=today.weekday())
    week_attendance = await db.execute(
        select(
            Attendance.date,
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date >= week_start
        ).group_by(Attendance.date).order_by(Attendance.date)
    )
    weekly_trend = [
        {
            "date": str(row.date),
            "total": row.total,
            "present": row.present or 0,
            "rate": round(((row.present or 0) / (row.total or 1)) * 100, 1)
        }
        for row in week_attendance.fetchall()
    ]
    
    # Get pending reports
    reports_result = await db.execute(
        select(func.count(Report.id)).where(
            Report.created_by == current_user.id,
            Report.status == 'pending'
        )
    )
    pending_reports = reports_result.scalar() or 0
    
    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "code": group.name,  # Using name as code identifier
            "students_count": students_count
        },
        "today_attendance": {
            "total": today_stats.total or 0,
            "present": today_stats.present or 0,
            "rate": round(((today_stats.present or 0) / (students_count or 1)) * 100, 1)
        },
        "weekly_trend": weekly_trend,
        "pending_reports": pending_reports
    }


@router.get("/admin")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get admin dashboard data.
    """
    # Get counts
    groups_count = await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )
    students_count = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    leaders_count = await db.execute(
        select(func.count(User.id)).where(
            User.role == UserRole.LEADER,
            User.is_active == True
        )
    )
    
    # Today's stats
    today = date.today()
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).where(Attendance.date == today)
    )
    today_stats = today_attendance.first()
    
    # Pending reports
    pending_reports = await db.execute(
        select(func.count(Report.id)).where(Report.status == 'pending')
    )
    
    # Low attendance groups (below 80%)
    week_start = today - timedelta(days=7)
    low_attendance_groups = await db.execute(
        select(
            Group.id,
            Group.name,
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).join(Student, Student.group_id == Group.id)
        .join(Attendance, Attendance.student_id == Student.id)
        .where(Attendance.date >= week_start)
        .group_by(Group.id)
        .having(
            (func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)) / 
             func.count(Attendance.id) * 100) < 80
        )
    )
    
    return {
        "stats": {
            "groups": groups_count.scalar() or 0,
            "students": students_count.scalar() or 0,
            "leaders": leaders_count.scalar() or 0
        },
        "today_attendance": {
            "total": today_stats.total or 0,
            "present": today_stats.present or 0,
            "rate": round(((today_stats.present or 0) / (today_stats.total or 1)) * 100, 1)
        },
        "pending_reports": pending_reports.scalar() or 0,
        "low_attendance_groups": [
            {
                "id": row.id,
                "name": row.name,
                "rate": round(((row.present or 0) / (row.total or 1)) * 100, 1)
            }
            for row in low_attendance_groups.fetchall()
        ]
    }


@router.get("/superadmin")
async def get_superadmin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """
    Get superadmin dashboard data.
    """
    # System stats
    users_count = await db.execute(select(func.count(User.id)))
    admins_count = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    )
    groups_count = await db.execute(select(func.count(Group.id)))
    students_count = await db.execute(select(func.count(Student.id)))
    
    # User distribution by role
    role_distribution = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    
    # Recent activity (simplified)
    today = date.today()
    week_start = today - timedelta(days=7)
    
    # Attendance trend
    attendance_trend = await db.execute(
        select(
            Attendance.date,
            func.count(Attendance.id).label('total'),
            func.sum(func.cast(Attendance.status == AttendanceStatus.PRESENT, int)).label('present')
        ).where(Attendance.date >= week_start)
        .group_by(Attendance.date)
        .order_by(Attendance.date)
    )
    
    return {
        "system_stats": {
            "total_users": users_count.scalar() or 0,
            "admins": admins_count.scalar() or 0,
            "groups": groups_count.scalar() or 0,
            "students": students_count.scalar() or 0
        },
        "role_distribution": {
            row[0].value: row[1]
            for row in role_distribution.fetchall()
        },
        "attendance_trend": [
            {
                "date": str(row.date),
                "total": row.total,
                "present": row.present or 0,
                "rate": round(((row.present or 0) / (row.total or 1)) * 100, 1)
            }
            for row in attendance_trend.fetchall()
        ]
    }


@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard summary based on user role.
    """
    if current_user.role == UserRole.SUPERADMIN:
        return await get_superadmin_dashboard(db, current_user)
    elif current_user.role == UserRole.ADMIN:
        return await get_admin_dashboard(db, current_user)
    elif current_user.role == UserRole.LEADER:
        return await get_leader_dashboard(db, current_user)
    else:
        return await get_student_dashboard(db, current_user)
