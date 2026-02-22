"""
UniControl - Mobile Dashboard Routes
=====================================
Unified dashboard endpoint for all roles.

Author: UniControl Team
Version: 2.0.0
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Schedule, WeekDay
from app.models.notification import Notification
from app.models.report import Report
from app.core.dependencies import get_current_active_user
from app.config import today_tashkent

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Unified dashboard stats endpoint.
    Returns data based on the user's role.
    """
    role = current_user.role

    if role == UserRole.STUDENT:
        return await _student_dashboard(db, current_user)
    elif role == UserRole.LEADER:
        return await _leader_dashboard(db, current_user)
    elif role == UserRole.TEACHER:
        return await _teacher_dashboard(db, current_user)
    elif role == UserRole.DEAN:
        return await _dean_dashboard(db, current_user)
    elif role == UserRole.REGISTRAR_OFFICE:
        return await _registrar_dashboard(db, current_user)
    elif role == UserRole.ACADEMIC_AFFAIRS:
        return await _academic_dashboard(db, current_user)
    elif role in (UserRole.ADMIN, UserRole.SUPERADMIN):
        return await _admin_dashboard(db, current_user)
    else:
        return await _student_dashboard(db, current_user)


async def _student_dashboard(db: AsyncSession, user: User):
    """Student dashboard stats."""
    result = await db.execute(
        select(Student).where(Student.user_id == user.id)
    )
    student = result.scalar_one_or_none()

    today = today_tashkent()
    month_start = today.replace(day=1)

    # Defaults
    data = {
        "role": "student",
        "total_students": 0,
        "total_groups": 0,
        "active_students": 0,
        "active_groups": 0,
        "today_present": 0,
        "today_absent": 0,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": 0.0,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "unread_notifications": 0,
        "today_lessons": 0,
        "pending_reports": 0,
    }

    if not student:
        return data

    # This month's stats
    month_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.EXCUSED, 1), else_=0)).label("excused"),
        ).where(
            Attendance.student_id == student.id,
            Attendance.date >= month_start,
        )
    )
    stats = month_stats.first()
    total = stats.total or 0
    present = stats.present or 0
    absent = stats.absent or 0
    late = stats.late or 0
    excused = stats.excused or 0

    # Today's attendance
    today_att = await db.execute(
        select(Attendance).where(
            Attendance.student_id == student.id,
            Attendance.date == today,
        )
    )
    today_record = today_att.scalar_one_or_none()
    if today_record:
        if today_record.status == AttendanceStatus.PRESENT:
            data["today_present"] = 1
        elif today_record.status == AttendanceStatus.ABSENT:
            data["today_absent"] = 1
        elif today_record.status == AttendanceStatus.LATE:
            data["today_late"] = 1
        elif today_record.status == AttendanceStatus.EXCUSED:
            data["today_excused"] = 1

    data["month_attendance_rate"] = round((present / total * 100) if total > 0 else 0.0, 1)

    # Week rate
    week_start = today - timedelta(days=today.weekday())
    week_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        ).where(
            Attendance.student_id == student.id,
            Attendance.date >= week_start,
        )
    )
    ws = week_stats.first()
    data["week_attendance_rate"] = round(((ws.present or 0) / (ws.total or 1)) * 100, 1)

    data["today_attendance_rate"] = data["month_attendance_rate"]

    # Today's lessons
    try:
        weekday = WeekDay(today.strftime("%A").lower())
        schedule_count = await db.execute(
            select(func.count(Schedule.id)).where(
                Schedule.group_id == student.group_id,
                Schedule.day_of_week == weekday,
                Schedule.is_active == True,
            )
        )
        data["today_lessons"] = schedule_count.scalar() or 0
    except Exception:
        data["today_lessons"] = 0

    # Unread notifications
    unread = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read == False,
        )
    )
    data["unread_notifications"] = unread.scalar() or 0

    return data


async def _leader_dashboard(db: AsyncSession, user: User):
    """Leader dashboard stats."""
    result = await db.execute(
        select(Group).where(Group.leader_id == user.id)
    )
    group = result.scalar_one_or_none()

    today = today_tashkent()
    month_start = today.replace(day=1)

    data = {
        "role": "leader",
        "total_students": 0,
        "total_groups": 1,
        "active_students": 0,
        "active_groups": 1,
        "today_present": 0,
        "today_absent": 0,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": 0.0,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "unread_notifications": 0,
        "today_lessons": 0,
        "pending_reports": 0,
    }

    if not group:
        return data

    # Students count
    students_count = await db.execute(
        select(func.count(Student.id)).where(
            Student.group_id == group.id,
            Student.is_active == True,
        )
    )
    data["total_students"] = students_count.scalar() or 0
    data["active_students"] = data["total_students"]

    # Today's attendance
    today_stats = await db.execute(
        select(
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.EXCUSED, 1), else_=0)).label("excused"),
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date == today,
        )
    )
    ts = today_stats.first()
    data["today_present"] = ts.present or 0
    data["today_absent"] = ts.absent or 0
    data["today_late"] = ts.late or 0
    data["today_excused"] = ts.excused or 0
    today_total = data["today_present"] + data["today_absent"] + data["today_late"] + data["today_excused"]
    data["today_attendance_rate"] = round((data["today_present"] / today_total * 100) if today_total > 0 else 0.0, 1)

    # Month attendance rate
    month_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date >= month_start,
        )
    )
    ms = month_stats.first()
    data["month_attendance_rate"] = round(((ms.present or 0) / (ms.total or 1)) * 100, 1)

    # Week rate
    week_start = today - timedelta(days=today.weekday())
    week_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        ).join(Student).where(
            Student.group_id == group.id,
            Attendance.date >= week_start,
        )
    )
    ws = week_stats.first()
    data["week_attendance_rate"] = round(((ws.present or 0) / (ws.total or 1)) * 100, 1)

    # Today's classes
    try:
        weekday = WeekDay(today.strftime("%A").lower())
        schedule_count = await db.execute(
            select(func.count(Schedule.id)).where(
                Schedule.group_id == group.id,
                Schedule.day_of_week == weekday,
                Schedule.is_active == True,
            )
        )
        data["today_lessons"] = schedule_count.scalar() or 0
    except Exception:
        data["today_lessons"] = 0

    # Unread notifications
    unread = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read == False,
        )
    )
    data["unread_notifications"] = unread.scalar() or 0

    return data


async def _admin_dashboard(db: AsyncSession, user: User):
    """Admin/SuperAdmin dashboard stats."""
    today = today_tashkent()
    month_start = today.replace(day=1)

    # Counts
    total_students = (await db.execute(select(func.count(Student.id)))).scalar() or 0
    active_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0
    total_groups = (await db.execute(select(func.count(Group.id)))).scalar() or 0
    active_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )).scalar() or 0

    # Today's attendance
    today_stats = await db.execute(
        select(
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.EXCUSED, 1), else_=0)).label("excused"),
        ).where(Attendance.date == today)
    )
    ts = today_stats.first()
    today_present = ts.present or 0
    today_absent = ts.absent or 0
    today_late = ts.late or 0
    today_excused = ts.excused or 0
    today_total = today_present + today_absent + today_late + today_excused
    today_rate = round((today_present / today_total * 100) if today_total > 0 else 0.0, 1)

    # Month rate
    month_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        ).where(Attendance.date >= month_start)
    )
    ms = month_stats.first()
    month_rate = round(((ms.present or 0) / (ms.total or 1)) * 100, 1)

    # Week rate
    week_start = today - timedelta(days=today.weekday())
    week_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        ).where(Attendance.date >= week_start)
    )
    ws = week_stats.first()
    week_rate = round(((ws.present or 0) / (ws.total or 1)) * 100, 1)

    # Unread notifications
    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read == False,
        )
    )).scalar() or 0

    # Pending reports
    try:
        from app.models.report import ReportStatus
        pending = (await db.execute(
            select(func.count(Report.id)).where(Report.status == ReportStatus.PENDING)
        )).scalar() or 0
    except Exception:
        pending = 0

    return {
        "role": user.role.value,
        "total_students": total_students,
        "total_groups": total_groups,
        "active_students": active_students,
        "active_groups": active_groups,
        "today_present": today_present,
        "today_absent": today_absent,
        "today_late": today_late,
        "today_excused": today_excused,
        "today_attendance_rate": today_rate,
        "week_attendance_rate": week_rate,
        "month_attendance_rate": month_rate,
        "unread_notifications": unread,
        "pending_reports": pending,
        "today_lessons": 0,
    }


# ============================================
# TEACHER DASHBOARD
# ============================================

async def _teacher_dashboard(db: AsyncSession, user: User):
    """Teacher dashboard stats for mobile."""
    from app.models.schedule import Schedule, WeekDay
    from sqlalchemy import distinct
    from sqlalchemy.orm import joinedload

    today = today_tashkent()
    day_map = {
        0: WeekDay.MONDAY, 1: WeekDay.TUESDAY, 2: WeekDay.WEDNESDAY,
        3: WeekDay.THURSDAY, 4: WeekDay.FRIDAY, 5: WeekDay.SATURDAY,
        6: WeekDay.SUNDAY,
    }
    today_weekday = day_map[today.weekday()]

    # Group IDs from schedule
    gids_result = await db.execute(
        select(distinct(Schedule.group_id)).where(
            Schedule.teacher_id == user.id, Schedule.is_active == True
        )
    )
    group_ids = [r[0] for r in gids_result.all()]

    total_students = 0
    if group_ids:
        total_students = (await db.execute(
            select(func.count(Student.id)).where(
                Student.group_id.in_(group_ids), Student.is_active == True
            )
        )).scalar() or 0

    # Today's lessons count
    today_lessons = (await db.execute(
        select(func.count(Schedule.id)).where(
            Schedule.teacher_id == user.id,
            Schedule.is_active == True,
            Schedule.is_cancelled == False,
            Schedule.day_of_week == today_weekday,
        )
    )).scalar() or 0

    weekly_lessons = (await db.execute(
        select(func.count(Schedule.id)).where(
            Schedule.teacher_id == user.id,
            Schedule.is_active == True,
            Schedule.is_cancelled == False,
        )
    )).scalar() or 0

    # Today's attendance rate for my groups
    today_attendance_rate = 0.0
    if group_ids:
        total_att = (await db.execute(
            select(func.count(Attendance.id))
            .join(Student, Student.id == Attendance.student_id)
            .where(Attendance.date == today, Student.group_id.in_(group_ids))
        )).scalar() or 0
        present_att = (await db.execute(
            select(func.count(Attendance.id))
            .join(Student, Student.id == Attendance.student_id)
            .where(
                Attendance.date == today,
                Student.group_id.in_(group_ids),
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
            )
        )).scalar() or 0
        if total_att > 0:
            today_attendance_rate = round(present_att / total_att * 100, 1)

    # Unread notifications
    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
    )).scalar() or 0

    return {
        "role": "teacher",
        "total_groups": len(group_ids),
        "total_students": total_students,
        "today_lessons": today_lessons,
        "weekly_lessons": weekly_lessons,
        "today_attendance_rate": today_attendance_rate,
        "unread_notifications": unread,
        "today_present": 0,
        "today_absent": 0,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": today_attendance_rate,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "pending_reports": 0,
        "active_students": total_students,
        "active_groups": len(group_ids),
    }


# ============================================
# DEAN DASHBOARD
# ============================================

async def _dean_dashboard(db: AsyncSession, user: User):
    """Dean dashboard stats for mobile."""
    today = today_tashkent()

    total_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0
    total_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )).scalar() or 0

    att_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.sum(case((Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]), 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
        ).where(Attendance.date == today)
    )
    row = att_stats.first()
    total_today = row.total or 0
    present = row.present or 0
    absent = row.absent or 0
    rate = round(present / total_today * 100, 1) if total_today > 0 else 0

    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
    )).scalar() or 0

    return {
        "role": "dean",
        "total_students": total_students,
        "total_groups": total_groups,
        "active_students": total_students,
        "active_groups": total_groups,
        "today_present": present,
        "today_absent": absent,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": rate,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "unread_notifications": unread,
        "today_lessons": 0,
        "pending_reports": 0,
    }


# ============================================
# REGISTRAR DASHBOARD
# ============================================

async def _registrar_dashboard(db: AsyncSession, user: User):
    """Registrar dashboard stats for mobile."""
    from app.models.nb_permit import NBPermit, PermitStatus

    today = today_tashkent()

    total_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0
    total_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )).scalar() or 0

    today_present = (await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.date == today, Attendance.status == AttendanceStatus.PRESENT
        )
    )).scalar() or 0
    today_absent = (await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.date == today, Attendance.status == AttendanceStatus.ABSENT
        )
    )).scalar() or 0

    active_permits = 0
    try:
        active_permits = (await db.execute(
            select(func.count(NBPermit.id)).where(
                NBPermit.status.in_([PermitStatus.ISSUED, PermitStatus.PENDING, PermitStatus.IN_PROGRESS])
            )
        )).scalar() or 0
    except Exception:
        pass

    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
    )).scalar() or 0

    return {
        "role": "registrar",
        "total_students": total_students,
        "total_groups": total_groups,
        "active_students": total_students,
        "active_groups": total_groups,
        "today_present": today_present,
        "today_absent": today_absent,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": round(today_present / (today_present + today_absent) * 100, 1) if (today_present + today_absent) > 0 else 0,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "unread_notifications": unread,
        "today_lessons": 0,
        "pending_reports": active_permits,
    }


# ============================================
# ACADEMIC AFFAIRS DASHBOARD
# ============================================

async def _academic_dashboard(db: AsyncSession, user: User):
    """Academic affairs dashboard stats for mobile."""
    from app.models.schedule import Schedule
    from sqlalchemy import distinct

    total_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )).scalar() or 0
    total_schedules = (await db.execute(
        select(func.count(Schedule.id)).where(Schedule.is_active == True)
    )).scalar() or 0
    total_subjects = (await db.execute(
        select(func.count(distinct(Schedule.subject))).where(Schedule.is_active == True)
    )).scalar() or 0
    total_teachers = (await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.TEACHER, User.is_active == True)
    )).scalar() or 0
    total_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0

    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
    )).scalar() or 0

    return {
        "role": "academic_affairs",
        "total_students": total_students,
        "total_groups": total_groups,
        "active_students": total_students,
        "active_groups": total_groups,
        "today_present": 0,
        "today_absent": 0,
        "today_late": 0,
        "today_excused": 0,
        "today_attendance_rate": 0.0,
        "week_attendance_rate": 0.0,
        "month_attendance_rate": 0.0,
        "unread_notifications": unread,
        "today_lessons": total_schedules,
        "pending_reports": 0,
        "total_schedules": total_schedules,
        "total_subjects": total_subjects,
        "total_teachers": total_teachers,
    }
