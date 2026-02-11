"""
UniControl - Dashboard Routes
=============================
Dashboard data endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date, datetime, timedelta
from app.config import now_tashkent, today_tashkent, TASHKENT_TZ
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.notification import Notification
from app.models.report import Report, ReportStatus
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
    today = today_tashkent()
    month_start = today.replace(day=1)
    
    attendance_result = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present'),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('absent'),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label('late')
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
            "full_name": student.name,
            "group_id": student.group_id,
            "student_id": student.student_id
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
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Leader dashboard request from user: id={current_user.id}, login={current_user.login}, email={current_user.email}")
    
    # First find the student record associated with this user
    # Using login/student_id match or user_id in student record
    student_result = await db.execute(
        select(Student).where(
            (Student.student_id == current_user.login) | 
            (Student.user_id == current_user.id)
        )
    )
    student = student_result.scalar_one_or_none()
    
    logger.info(f"Found student: {student.id if student else 'None'}, student_id: {student.student_id if student else 'None'}, group_id: {student.group_id if student else 'None'}")
    
    group = None
    if student:
        # Get leader's group where this student is leader
        group_result = await db.execute(
            select(Group).where(Group.leader_id == student.id)
        )
        group = group_result.scalar_one_or_none()
        logger.info(f"Found group by leader_id: {group.name if group else 'None'}")
        
        # If not found by leader_id, try by student's group_id
        if not group and student.group_id:
            group_result = await db.execute(
                select(Group).where(Group.id == student.group_id)
            )
            group = group_result.scalar_one_or_none()
            logger.info(f"Found group by student group_id: {group.name if group else 'None'}")
    
    if not group:
        return {"error": "No group assigned", "user_login": current_user.login, "student_found": student is not None}
    
    # Get group students count
    students_result = await db.execute(
        select(func.count(Student.id)).where(
            Student.group_id == group.id,
            Student.is_active == True
        )
    )
    students_count = students_result.scalar() or 0
    
    # Get today's attendance
    today = today_tashkent()
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present')
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
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present')
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
            "students_count": students_count,
            "faculty": group.faculty,  # Yo'nalish (specialty)
            "specialty": group.faculty,  # Alias for frontend
            "course_year": group.course_year
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
    today = today_tashkent()
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present')
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
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present')
        ).join(Student, Student.group_id == Group.id)
        .join(Attendance, Attendance.student_id == Student.id)
        .where(Attendance.date >= week_start)
        .group_by(Group.id)
        .having(
            (func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)) / 
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
    Get superadmin dashboard data — comprehensive system overview.
    """
    
    today = today_tashkent()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)
    
    # ===== System Stats =====
    users_count = await db.execute(select(func.count(User.id)))
    active_users_count = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    admins_count = await db.execute(
        select(func.count(User.id)).where(
            User.role.in_([UserRole.ADMIN, UserRole.SUPERADMIN])
        )
    )
    leaders_count = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.LEADER)
    )
    groups_count = await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )
    total_groups = await db.execute(select(func.count(Group.id)))
    students_count = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    total_students = await db.execute(select(func.count(Student.id)))
    
    # ===== User Distribution =====
    role_distribution = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    
    # ===== Today Attendance =====
    today_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present'),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('absent'),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label('late')
        ).where(Attendance.date == today)
    )
    today_stats = today_attendance.first()
    
    # ===== This Month Attendance =====
    month_attendance = await db.execute(
        select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present'),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('absent'),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label('late')
        ).where(Attendance.date >= month_start)
    )
    month_stats = month_attendance.first()
    
    # ===== Weekly Attendance Trend =====
    attendance_trend = await db.execute(
        select(
            Attendance.date,
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present'),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('absent'),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label('late')
        ).where(Attendance.date >= week_start)
        .group_by(Attendance.date)
        .order_by(Attendance.date)
    )
    
    # ===== Reports Stats =====
    total_reports = await db.execute(select(func.count(Report.id)))
    pending_reports = await db.execute(
        select(func.count(Report.id)).where(Report.status == ReportStatus.PENDING)
    )
    
    # ===== Notifications =====
    total_notifications = await db.execute(select(func.count(Notification.id)))
    
    # ===== Top Groups by Student Count =====
    top_groups = await db.execute(
        select(
            Group.id,
            Group.name,
            Group.faculty,
            Group.course_year,
            func.count(Student.id).label('student_count')
        ).outerjoin(Student, Student.group_id == Group.id)
        .where(Group.is_active == True)
        .group_by(Group.id)
        .order_by(func.count(Student.id).desc())
        .limit(10)
    )
    
    # ===== Recent Users =====
    recent_users = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(5)
    )
    
    # ===== New users this week =====
    week_start_dt = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=TASHKENT_TZ)
    new_users_week = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_start_dt)
    )
    
    return {
        "system_stats": {
            "total_users": users_count.scalar() or 0,
            "active_users": active_users_count.scalar() or 0,
            "admins": admins_count.scalar() or 0,
            "leaders": leaders_count.scalar() or 0,
            "groups": groups_count.scalar() or 0,
            "total_groups": total_groups.scalar() or 0,
            "students": students_count.scalar() or 0,
            "total_students": total_students.scalar() or 0,
            "new_users_this_week": new_users_week.scalar() or 0
        },
        "role_distribution": {
            row[0].value: row[1]
            for row in role_distribution.fetchall()
        },
        "today_attendance": {
            "total": today_stats.total or 0,
            "present": today_stats.present or 0,
            "absent": today_stats.absent or 0,
            "late": today_stats.late or 0,
            "rate": round(((today_stats.present or 0) / max(today_stats.total or 1, 1)) * 100, 1)
        },
        "month_attendance": {
            "total": month_stats.total or 0,
            "present": month_stats.present or 0,
            "absent": month_stats.absent or 0,
            "late": month_stats.late or 0,
            "rate": round(((month_stats.present or 0) / max(month_stats.total or 1, 1)) * 100, 1)
        },
        "attendance_trend": [
            {
                "date": str(row.date),
                "total": row.total,
                "present": row.present or 0,
                "absent": row.absent or 0,
                "late": row.late or 0,
                "rate": round(((row.present or 0) / max(row.total or 1, 1)) * 100, 1)
            }
            for row in attendance_trend.fetchall()
        ],
        "reports": {
            "total": total_reports.scalar() or 0,
            "pending": pending_reports.scalar() or 0
        },
        "notifications_count": total_notifications.scalar() or 0,
        "top_groups": [
            {
                "id": row.id,
                "name": row.name,
                "faculty": row.faculty,
                "course_year": row.course_year,
                "student_count": row.student_count or 0
            }
            for row in top_groups.fetchall()
        ],
        "recent_users": [
            {
                "id": u.id,
                "name": u.name,
                "login": u.login,
                "role": u.role.value,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in recent_users.scalars().all()
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