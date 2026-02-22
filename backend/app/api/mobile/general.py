"""
UniControl - Mobile General Routes
=================================
Common mobile endpoints without /student or /leader prefix.

These provide group/notifications/students/attendance helpers used by the mobile app.
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
from app.config import today_tashkent, now_tashkent

router = APIRouter()


# ==========================================
# SCHEDULE
# ==========================================

@router.get("/schedule")
async def mobile_schedule(
    group_id: Optional[int] = Query(None),
    day: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return schedule for current user (student/leader) or for group if provided."""
    # Resolve group_id if not provided
    if not group_id:
        student_res = await db.execute(select(Student).where(Student.user_id == current_user.id))
        student = student_res.scalar_one_or_none()
        if student:
            group_id = student.group_id
        else:
            group_res = await db.execute(select(Group).where(Group.leader_id == current_user.id))
            group = group_res.scalar_one_or_none()
            if group:
                group_id = group.id

    if not group_id:
        return {"schedule": []}

    query = select(Schedule).where(
        Schedule.group_id == group_id,
        Schedule.is_active == True
    ).order_by(Schedule.day_of_week, Schedule.start_time)

    # Filter by day if specified
    if day:
        dn = day.strip().lower()
        try:
            wd = WeekDay(dn)
            query = select(Schedule).where(
                Schedule.group_id == group_id,
                Schedule.is_active == True,
                Schedule.day_of_week == wd,
            ).order_by(Schedule.start_time)
        except Exception:
            return {"schedule": [], "error": "Invalid day"}

    schedules = await db.execute(query)
    items = []
    for s in schedules.scalars().all():
        items.append({
            "id": s.id,
            "subject": s.subject,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "room": s.room,
            "teacher": s.teacher_name,
            "day_of_week": s.day_of_week.name,
            "day": s.day_of_week.name,
            "week_type": s.week_type.value if s.week_type else "all",
            "is_cancelled": s.is_cancelled,
        })
    return {"schedule": items}


@router.get("/schedule/today")
async def mobile_schedule_today(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get today's schedule for current user."""
    student_res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = student_res.scalar_one_or_none()

    group_id = None
    if student:
        group_id = student.group_id
    else:
        # Maybe leader
        group_res = await db.execute(select(Group).where(Group.leader_id == current_user.id))
        group = group_res.scalar_one_or_none()
        if group:
            group_id = group.id

    today = today_tashkent()
    day_name = today.strftime("%A").upper()

    if not group_id:
        return {"date": str(today), "day": day_name, "classes": []}

    try:
        weekday = WeekDay(today.strftime("%A").lower())
    except Exception:
        return {"date": str(today), "day": day_name, "classes": []}

    schedules = await db.execute(
        select(Schedule).where(
            Schedule.group_id == group_id,
            Schedule.day_of_week == weekday,
            Schedule.is_active == True,
        ).order_by(Schedule.start_time)
    )

    return {
        "date": str(today),
        "day": weekday.name,
        "classes": [
            {
                "id": s.id,
                "subject": s.subject,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "room": s.room,
                "teacher": s.teacher_name,
                "week_type": s.week_type.value if s.week_type else "all",
                "is_cancelled": s.is_cancelled,
            }
            for s in schedules.scalars().all()
        ],
    }


@router.get("/schedule/week")
async def mobile_schedule_week(
    group_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get full weekly schedule."""
    if not group_id:
        student_res = await db.execute(select(Student).where(Student.user_id == current_user.id))
        student = student_res.scalar_one_or_none()
        if student:
            group_id = student.group_id
        else:
            group_res = await db.execute(select(Group).where(Group.leader_id == current_user.id))
            group = group_res.scalar_one_or_none()
            if group:
                group_id = group.id

    today = today_tashkent()
    # Calculate Monday of current week
    week_start = today - timedelta(days=today.weekday())

    if not group_id:
        return {
            "week_start": str(week_start),
            "days": [
                {"day": d.name, "date": str(week_start + timedelta(days=i)), "classes": []}
                for i, d in enumerate(WeekDay)
            ],
        }

    schedules = await db.execute(
        select(Schedule).where(
            Schedule.group_id == group_id,
            Schedule.is_active == True,
        ).order_by(Schedule.day_of_week, Schedule.start_time)
    )

    week_data = {}
    for d in WeekDay:
        week_data[d.name] = []

    for s in schedules.scalars().all():
        week_data[s.day_of_week.name].append({
            "id": s.id,
            "subject": s.subject,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "room": s.room,
            "teacher": s.teacher_name,
            "week_type": s.week_type.value if s.week_type else "all",
            "is_cancelled": s.is_cancelled,
        })

    return {
        "week_start": str(week_start),
        "days": [
            {
                "day": d.name,
                "date": str(week_start + timedelta(days=i)),
                "classes": week_data.get(d.name, []),
            }
            for i, d in enumerate(WeekDay)
        ],
    }


# ==========================================
# ATTENDANCE
# ==========================================

@router.get("/attendance")
async def mobile_attendance(
    student_id: Optional[int] = Query(None),
    group_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return attendance records with flexible filtering."""
    query = select(Attendance)

    # Determine student_id if not provided
    if student_id:
        query = query.where(Attendance.student_id == student_id)
    elif group_id:
        # Get all students in group
        query = query.join(Student).where(Student.group_id == group_id)
    else:
        # Default to current student
        row = await db.execute(select(Student).where(Student.user_id == current_user.id))
        student = row.scalar_one_or_none()
        if student:
            query = query.where(Attendance.student_id == student.id)
        else:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

    # Date filtering
    if date_from:
        try:
            from datetime import datetime
            df = datetime.strptime(date_from, "%Y-%m-%d").date()
            query = query.where(Attendance.date >= df)
        except Exception:
            pass
    elif date_to:
        pass  # Only apply date_from if provided
    else:
        start_date = today_tashkent() - timedelta(days=days)
        query = query.where(Attendance.date >= start_date)

    if date_to:
        try:
            from datetime import datetime
            dt = datetime.strptime(date_to, "%Y-%m-%d").date()
            query = query.where(Attendance.date <= dt)
        except Exception:
            pass

    if status:
        try:
            status_enum = AttendanceStatus(status)
            query = query.where(Attendance.status == status_enum)
        except Exception:
            pass

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Attendance.date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    items = []
    for a in records:
        items.append({
            "id": a.id,
            "student_id": a.student_id,
            "student_name": None,  # Will be filled if needed
            "group_id": None,
            "date": str(a.date),
            "status": a.status.value,
            "reason": a.excuse_reason if hasattr(a, "excuse_reason") else None,
            "notes": a.note,
            "marked_by": a.recorded_by,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/attendance/batch")
async def mobile_attendance_batch(
    records: list[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """Batch create/update attendance records."""
    marked = 0
    errors = []

    for record in records:
        try:
            sid = record["student_id"]
            att_date = record.get("date", str(today_tashkent()))
            if isinstance(att_date, str):
                from datetime import datetime
                att_date = datetime.strptime(att_date, "%Y-%m-%d").date()
            status = AttendanceStatus(record["status"])

            existing = await db.execute(
                select(Attendance).where(
                    Attendance.student_id == sid,
                    Attendance.date == att_date,
                )
            )
            att = existing.scalar_one_or_none()

            if att:
                att.status = status
                att.recorded_by = current_user.id
            else:
                att = Attendance(
                    student_id=sid,
                    date=att_date,
                    status=status,
                    recorded_by=current_user.id,
                )
                db.add(att)

            marked += 1
        except Exception as e:
            errors.append(f"Student {record.get('student_id')}: {str(e)}")

    await db.commit()
    return {"marked": marked, "errors": errors}


@router.get("/attendance/stats")
async def mobile_attendance_stats(
    student_id: Optional[int] = Query(None),
    group_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get attendance statistics."""
    from sqlalchemy import case

    start_date = today_tashkent() - timedelta(days=days)
    query = select(
        func.count(Attendance.id).label("total"),
        func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
        func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
        func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
        func.sum(case((Attendance.status == AttendanceStatus.EXCUSED, 1), else_=0)).label("excused"),
    ).where(Attendance.date >= start_date)

    if student_id:
        query = query.where(Attendance.student_id == student_id)
    elif group_id:
        query = query.join(Student).where(Student.group_id == group_id)
    else:
        row = await db.execute(select(Student).where(Student.user_id == current_user.id))
        student = row.scalar_one_or_none()
        if student:
            query = query.where(Attendance.student_id == student.id)

    result = await db.execute(query)
    stats = result.first()

    total = stats.total or 0
    present = stats.present or 0
    absent = stats.absent or 0
    late_count = stats.late or 0
    excused = stats.excused or 0

    return {
        "total": total,
        "present": present,
        "absent": absent,
        "late": late_count,
        "excused": excused,
        "attendance_rate": round((present / total * 100) if total > 0 else 0.0, 1),
    }


# ==========================================
# GROUPS
# ==========================================

@router.get("/groups")
async def mobile_groups(
    search: Optional[str] = Query(None),
    active_only: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List groups."""
    query = select(Group)

    if active_only:
        query = query.where(Group.is_active == True)
    if search:
        query = query.where(Group.name.ilike(f"%{search}%"))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Group.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    res = await db.execute(query)
    groups = res.scalars().all()

    items = []
    for g in groups:
        # Count students
        sc = await db.execute(
            select(func.count(Student.id)).where(
                Student.group_id == g.id,
                Student.is_active == True,
            )
        )
        student_count = sc.scalar() or 0

        # Leader name
        leader_name = None
        if g.leader_id:
            lr = await db.execute(select(Student).where(Student.id == g.leader_id))
            leader_student = lr.scalar_one_or_none()
            if leader_student:
                leader_name = leader_student.full_name

        items.append({
            "id": g.id,
            "name": g.name,
            "direction_id": g.direction_id if hasattr(g, "direction_id") else None,
            "direction_name": g.direction_name if hasattr(g, "direction_name") else None,
            "course": g.course if hasattr(g, "course") else None,
            "leader_id": g.leader_id,
            "leader_name": leader_name,
            "student_count": student_count,
            "is_active": g.is_active,
            "is_blocked": g.is_blocked if hasattr(g, "is_blocked") else False,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/groups/{group_id}")
async def mobile_group_detail(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get group detail."""
    res = await db.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    sc = await db.execute(
        select(func.count(Student.id)).where(
            Student.group_id == group.id,
            Student.is_active == True,
        )
    )
    student_count = sc.scalar() or 0

    leader_name = None
    if group.leader_id:
        lr = await db.execute(select(Student).where(Student.id == group.leader_id))
        leader_student = lr.scalar_one_or_none()
        if leader_student:
            leader_name = leader_student.full_name

    return {
        "id": group.id,
        "name": group.name,
        "direction_id": group.direction_id if hasattr(group, "direction_id") else None,
        "direction_name": group.direction_name if hasattr(group, "direction_name") else None,
        "course": group.course if hasattr(group, "course") else None,
        "leader_id": group.leader_id,
        "leader_name": leader_name,
        "student_count": student_count,
        "is_active": group.is_active,
    }


@router.get("/groups/{group_id}/students")
async def mobile_group_students(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get students in a group."""
    res = await db.execute(
        select(Student).where(
            Student.group_id == group_id,
            Student.is_active == True,
        ).order_by(Student.name)
    )
    students = res.scalars().all()

    return {
        "items": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "name": s.name,
                "full_name": s.full_name,
                "phone": s.phone,
                "email": s.email,
                "is_active": s.is_active,
            }
            for s in students
        ]
    }


# ==========================================
# STUDENTS
# ==========================================

@router.get("/students")
async def mobile_students(
    search: Optional[str] = Query(None),
    group_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List students for mobile."""
    query = select(Student).where(Student.is_active == True)

    if group_id:
        query = query.where(Student.group_id == group_id)
    if search:
        query = query.where(Student.name.ilike(f"%{search}%"))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Student.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    students = result.scalars().all()

    items = []
    for s in students:
        items.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "user_id": s.user_id,
            "group_id": s.group_id,
            "group_name": s.group_name,
            "phone": s.phone,
            "email": s.email,
            "gender": s.gender,
            "contract_amount": float(s.contract_amount) if s.contract_amount else None,
            "contract_paid": float(s.contract_paid) if s.contract_paid else None,
            "is_active": s.is_active,
            "is_graduated": s.is_graduated,
            "avatar": s.avatar,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/students/{student_id}")
async def mobile_student_detail(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get student detail."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    return {
        "id": student.id,
        "student_id": student.student_id,
        "name": student.name,
        "user_id": student.user_id,
        "group_id": student.group_id,
        "group_name": student.group_name,
        "phone": student.phone,
        "email": student.email,
        "address": student.address,
        "commute": student.commute,
        "passport": student.passport,
        "jshshir": student.jshshir,
        "birth_date": student.birth_date.isoformat() if student.birth_date else None,
        "gender": student.gender,
        "contract_amount": float(student.contract_amount) if student.contract_amount else None,
        "contract_paid": float(student.contract_paid) if student.contract_paid else None,
        "enrollment_date": student.enrollment_date.isoformat() if student.enrollment_date else None,
        "graduation_date": student.graduation_date.isoformat() if student.graduation_date else None,
        "is_active": student.is_active,
        "is_graduated": student.is_graduated,
        "avatar": student.avatar,
        "created_at": student.created_at.isoformat() if student.created_at else None,
    }


# ==========================================
# NOTIFICATIONS
# ==========================================

@router.get("/notifications")
async def mobile_notifications(
    unread_only: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get notifications for current user."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Notification.is_read, Notification.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return {
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type.value if n.type else "info",
                "is_read": n.is_read,
                "sender_id": n.sender_id if hasattr(n, "sender_id") else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "read_at": n.read_at.isoformat() if hasattr(n, "read_at") and n.read_at else None,
            }
            for n in notifications
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/notifications/unread-count")
async def mobile_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get unread notification count."""
    res = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    count = res.scalar() or 0
    return {"count": count}


@router.put("/notifications/{notification_id}/read")
@router.post("/notifications/{notification_id}/read")
async def mobile_mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")

    notification.is_read = True
    if hasattr(notification, "read_at"):
        notification.read_at = now_tashkent()
    await db.commit()

    return {"message": "O'qildi deb belgilandi"}


@router.put("/notifications/read-all")
@router.post("/notifications/read-all")
async def mobile_mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark all notifications as read."""
    from sqlalchemy import update

    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    await db.commit()

    return {"message": "Barcha bildirishnomalar o'qildi deb belgilandi"}
