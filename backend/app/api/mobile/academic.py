"""
UniControl - Mobile Academic Affairs Panel
============================================
Academic affairs mobile endpoints (read-only):
dashboard, groups, schedule, exams, faculties, teachers.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct, case
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import Schedule, WeekDay
from app.models.group import Group
from app.models.student import Student
from app.models.teacher_workload import TeacherWorkload
from app.core.dependencies import get_current_active_user
from app.config import today_tashkent

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_mobile_academic(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require academic_affairs role for mobile."""
    if current_user.role not in [
        UserRole.ACADEMIC_AFFAIRS,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ]:
        raise HTTPException(status_code=403, detail="Akademik ishlar ruxsati kerak")
    return current_user


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def mobile_academic_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Academic affairs mobile dashboard."""
    total_groups = (
        await db.execute(
            select(func.count(Group.id)).where(Group.is_active == True)
        )
    ).scalar() or 0

    total_schedules = (
        await db.execute(
            select(func.count(Schedule.id)).where(Schedule.is_active == True)
        )
    ).scalar() or 0

    total_subjects = (
        await db.execute(
            select(func.count(distinct(Schedule.subject))).where(
                Schedule.is_active == True
            )
        )
    ).scalar() or 0

    total_teachers = (
        await db.execute(
            select(func.count(User.id)).where(
                and_(User.role == UserRole.TEACHER, User.is_active == True)
            )
        )
    ).scalar() or 0

    total_students = (
        await db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
    ).scalar() or 0

    # Groups without schedule
    groups_with_schedule = (
        await db.execute(
            select(distinct(Schedule.group_id)).where(Schedule.is_active == True)
        )
    ).scalars().all()
    if groups_with_schedule:
        groups_without = (
            await db.execute(
                select(func.count(Group.id)).where(
                    and_(
                        Group.is_active == True,
                        ~Group.id.in_(groups_with_schedule),
                    )
                )
            )
        ).scalar() or 0
    else:
        groups_without = total_groups

    return {
        "role": "academic_affairs",
        "total_groups": total_groups,
        "total_schedules": total_schedules,
        "total_subjects": total_subjects,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "groups_without_schedule": groups_without,
    }


# ============================================
# GROUPS
# ============================================

@router.get("/groups")
async def mobile_academic_groups(
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get groups with student count and schedule status."""
    query = (
        select(
            Group,
            func.count(Student.id).label("students_count"),
        )
        .outerjoin(
            Student, and_(Student.group_id == Group.id, Student.is_active == True)
        )
        .where(Group.is_active == True)
    )

    if faculty:
        query = query.where(Group.faculty == faculty)
    if course_year:
        query = query.where(Group.course_year == course_year)
    if search:
        query = query.where(Group.name.ilike(f"%{search}%"))

    query = query.group_by(Group.id).order_by(Group.name)

    # Count
    all_result = await db.execute(query)
    all_rows = all_result.all()
    total = len(all_rows)

    # Paginate manually (GROUP BY makes offset/limit tricky with some ORMs)
    offset = (page - 1) * per_page
    page_rows = all_rows[offset : offset + per_page]

    # Check which groups have schedules
    schedule_group_ids = set(
        (
            await db.execute(
                select(distinct(Schedule.group_id)).where(Schedule.is_active == True)
            )
        ).scalars().all()
    )

    items = []
    for g, cnt in page_rows:
        items.append(
            {
                "id": g.id,
                "name": g.name,
                "faculty": g.faculty,
                "course_year": g.course_year,
                "students_count": cnt or 0,
                "has_schedule": g.id in schedule_group_ids,
            }
        )

    return {"groups": items, "total": total, "page": page}


# ============================================
# SCHEDULE (read-only)
# ============================================

@router.get("/schedule")
async def mobile_academic_schedule(
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    teacher: Optional[str] = None,
    day: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get schedules (read-only)."""
    query = (
        select(Schedule)
        .options(joinedload(Schedule.group))
        .where(Schedule.is_active == True)
    )

    if group_id:
        query = query.where(Schedule.group_id == group_id)
    if faculty:
        fac_subq = select(Group.id).where(
            and_(Group.is_active == True, Group.faculty == faculty)
        ).scalar_subquery()
        query = query.where(Schedule.group_id.in_(fac_subq))
    if teacher:
        query = query.where(Schedule.teacher_name.ilike(f"%{teacher}%"))
    if day:
        try:
            wd = WeekDay(day.strip().lower())
            query = query.where(Schedule.day_of_week == wd)
        except ValueError:
            pass

    total = (
        await db.execute(select(func.count()).select_from(query.subquery()))
    ).scalar() or 0

    query = (
        query.order_by(Schedule.day_of_week, Schedule.start_time)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    schedules = result.unique().scalars().all()

    items = []
    for s in schedules:
        items.append(
            {
                "id": s.id,
                "subject": s.subject,
                "subject_code": s.subject_code,
                "group_id": s.group_id,
                "group_name": s.group.name if s.group else None,
                "teacher_name": s.teacher_name,
                "day_of_week": s.day_of_week.value if s.day_of_week else None,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "building": s.building,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
                "schedule_type": s.schedule_type.value if s.schedule_type else None,
                "is_cancelled": s.is_cancelled,
            }
        )

    return {"items": items, "total": total, "page": page}


@router.get("/schedule/group/{group_id}")
async def mobile_academic_schedule_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get full weekly schedule for a specific group."""
    result = await db.execute(
        select(Schedule)
        .where(and_(Schedule.group_id == group_id, Schedule.is_active == True))
        .order_by(Schedule.day_of_week, Schedule.start_time)
    )
    schedules = result.scalars().all()

    # Group by day
    week_schedule = {}
    for day in WeekDay:
        week_schedule[day.value] = []

    for s in schedules:
        day_key = s.day_of_week.value if s.day_of_week else "monday"
        week_schedule[day_key].append(
            {
                "id": s.id,
                "subject": s.subject,
                "teacher_name": s.teacher_name,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
                "schedule_type": s.schedule_type.value if s.schedule_type else None,
                "is_cancelled": s.is_cancelled,
            }
        )

    # Get group info
    group = await db.get(Group, group_id)
    group_info = {
        "id": group.id,
        "name": group.name,
        "faculty": group.faculty,
        "course_year": group.course_year,
    } if group else {}

    return {"group": group_info, "schedule": week_schedule, "total": len(schedules)}


# ============================================
# EXAMS (read-only)
# ============================================

@router.get("/exams")
async def mobile_academic_exams(
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get exam schedules (read-only)."""
    try:
        from app.models.exam_schedule import ExamSchedule

        query = select(ExamSchedule)

        if group_id:
            query = query.where(ExamSchedule.group_id == group_id)
        if faculty:
            fac_subq = select(Group.id).where(
                and_(Group.is_active == True, Group.faculty == faculty)
            ).scalar_subquery()
            query = query.where(ExamSchedule.group_id.in_(fac_subq))

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        query = (
            query.order_by(ExamSchedule.exam_date, ExamSchedule.start_time)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(query)
        exams = result.scalars().all()

        items = []
        for e in exams:
            items.append(
                {
                    "id": e.id,
                    "subject": e.subject,
                    "group_id": e.group_id,
                    "group_name": getattr(e, "group_name", ""),
                    "teacher_name": getattr(e, "teacher_name", ""),
                    "exam_date": str(e.exam_date) if e.exam_date else None,
                    "start_time": e.start_time.strftime("%H:%M") if getattr(e, "start_time", None) else None,
                    "end_time": e.end_time.strftime("%H:%M") if getattr(e, "end_time", None) else None,
                    "room": getattr(e, "room", ""),
                    "exam_type": getattr(e, "exam_type", ""),
                }
            )

        return {"items": items, "total": total, "page": page}

    except ImportError:
        return {"items": [], "total": 0}


# ============================================
# FACULTIES
# ============================================

@router.get("/faculties")
async def mobile_academic_faculties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get faculties with stats."""
    result = await db.execute(
        select(
            Group.faculty,
            func.count(distinct(Group.id)).label("groups_count"),
            func.count(Student.id).label("students_count"),
        )
        .outerjoin(
            Student, and_(Student.group_id == Group.id, Student.is_active == True)
        )
        .where(
            and_(
                Group.is_active == True,
                Group.faculty.isnot(None),
                Group.faculty != "",
            )
        )
        .group_by(Group.faculty)
        .order_by(Group.faculty)
    )
    rows = result.all()

    faculties = []
    for row in rows:
        faculties.append(
            {
                "name": row[0],
                "groups_count": row[1] or 0,
                "students_count": row[2] or 0,
            }
        )

    return {"faculties": faculties, "total": len(faculties)}


# ============================================
# TEACHERS
# ============================================

@router.get("/teachers")
async def mobile_academic_teachers(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get teachers list."""
    query = select(User).where(
        and_(User.role == UserRole.TEACHER, User.is_active == True)
    )
    if search:
        query = query.where(User.name.ilike(f"%{search}%"))

    query = query.order_by(User.name)
    result = await db.execute(query)
    teachers = result.scalars().all()

    items = []
    for t in teachers:
        items.append(
            {
                "id": t.id,
                "name": t.name,
                "email": t.email,
                "phone": t.phone,
            }
        )

    return {"teachers": items, "total": len(items)}


# ============================================
# WORKLOAD (read-only)
# ============================================

@router.get("/workload")
async def mobile_academic_workload(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get teacher workload."""
    query = select(TeacherWorkload).where(TeacherWorkload.is_active == True)

    if search:
        query = query.where(TeacherWorkload.teacher_name.ilike(f"%{search}%"))
    if department:
        query = query.where(TeacherWorkload.department.ilike(f"%{department}%"))

    query = query.order_by(
        TeacherWorkload.teacher_name,
        case(
            (TeacherWorkload.day_of_week == "monday", 1),
            (TeacherWorkload.day_of_week == "tuesday", 2),
            (TeacherWorkload.day_of_week == "wednesday", 3),
            (TeacherWorkload.day_of_week == "thursday", 4),
            (TeacherWorkload.day_of_week == "friday", 5),
            (TeacherWorkload.day_of_week == "saturday", 6),
            else_=7,
        ),
        TeacherWorkload.lesson_number,
    )

    result = await db.execute(query)
    workloads = result.scalars().all()

    items = []
    for w in workloads:
        items.append(
            {
                "id": w.id,
                "teacher_name": w.teacher_name,
                "department": w.department,
                "teacher_type": w.teacher_type,
                "day_of_week": w.day_of_week,
                "day_name_uz": w.day_name_uz,
                "lesson_number": w.lesson_number,
                "start_time": w.start_time,
                "end_time": w.end_time,
                "groups": w.groups,
                "is_busy": w.is_busy,
            }
        )

    return {"items": items, "total": len(items)}


@router.get("/workload/departments")
async def mobile_academic_workload_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_academic),
):
    """Get departments list from workload data."""
    result = await db.execute(
        select(distinct(TeacherWorkload.department))
        .where(
            and_(
                TeacherWorkload.is_active == True,
                TeacherWorkload.department.isnot(None),
                TeacherWorkload.department != "",
            )
        )
        .order_by(TeacherWorkload.department)
    )
    departments = [row[0] for row in result.all() if row[0]]
    return {"departments": departments}
