"""
UniControl - Mobile Dean Panel
================================
Read-only dean endpoints for mobile:
dashboard, students, groups, faculties, attendance, schedule,
contracts, NB permits, workload.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct, case
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import Schedule, WeekDay
from app.models.group import Group
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.teacher_workload import TeacherWorkload
from app.core.dependencies import get_current_active_user
from app.config import today_tashkent

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_mobile_dean(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require dean role for mobile."""
    if current_user.role not in [
        UserRole.DEAN,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ]:
        raise HTTPException(status_code=403, detail="Dekanat ruxsati kerak")
    return current_user


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def mobile_dean_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Dean mobile dashboard — students, attendance, NB stats."""
    today = today_tashkent()

    total_students = (
        await db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
    ).scalar() or 0

    total_groups = (
        await db.execute(
            select(func.count(Group.id)).where(Group.is_active == True)
        )
    ).scalar() or 0

    # Today's attendance
    att_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.count(Attendance.id)
            .filter(
                Attendance.status.in_(
                    [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                )
            )
            .label("present"),
            func.count(Attendance.id)
            .filter(Attendance.status == AttendanceStatus.ABSENT)
            .label("absent"),
        ).where(Attendance.date == today)
    )
    att_row = att_stats.one()
    total_today = att_row.total or 0
    present_count = att_row.present or 0
    absent_count = att_row.absent or 0
    attendance_rate = round(present_count / total_today * 100, 1) if total_today > 0 else 0

    # Today lessons
    day_map = {
        0: WeekDay.MONDAY, 1: WeekDay.TUESDAY, 2: WeekDay.WEDNESDAY,
        3: WeekDay.THURSDAY, 4: WeekDay.FRIDAY, 5: WeekDay.SATURDAY,
        6: WeekDay.SUNDAY,
    }
    today_weekday = day_map[today.weekday()]
    today_lessons = (
        await db.execute(
            select(func.count(Schedule.id)).where(
                and_(
                    Schedule.is_active == True,
                    Schedule.is_cancelled == False,
                    Schedule.day_of_week == today_weekday,
                )
            )
        )
    ).scalar() or 0

    # NB permits stats
    nb_stats = {"total": 0, "active": 0, "approved": 0}
    try:
        from app.models.nb_permit import NBPermit, PermitStatus

        nb_result = await db.execute(
            select(
                func.count(NBPermit.id).label("total"),
                func.count(NBPermit.id)
                .filter(
                    NBPermit.status.in_(
                        [PermitStatus.ISSUED, PermitStatus.PENDING, PermitStatus.IN_PROGRESS]
                    )
                )
                .label("active"),
                func.count(NBPermit.id)
                .filter(NBPermit.status == PermitStatus.APPROVED)
                .label("approved"),
            )
        )
        nb_row = nb_result.one()
        nb_stats = {
            "total": nb_row.total or 0,
            "active": nb_row.active or 0,
            "approved": nb_row.approved or 0,
        }
    except Exception:
        pass

    # Contract stats
    contract_stats = {"total": 0, "paid": 0, "debt": 0}
    try:
        from app.models.contract import Contract

        cr = await db.execute(
            select(
                func.count(Contract.id),
                func.coalesce(func.sum(Contract.total_paid), 0),
                func.coalesce(func.sum(Contract.contract_amount), 0),
            )
        )
        row = cr.one()
        contract_stats["total"] = row[0] or 0
        contract_stats["paid"] = float(row[1] or 0)
        contract_stats["debt"] = float((row[2] or 0) - (row[1] or 0))
    except Exception:
        pass

    return {
        "role": "dean",
        "total_students": total_students,
        "total_groups": total_groups,
        "today_present": present_count,
        "today_absent": absent_count,
        "attendance_rate": attendance_rate,
        "today_lessons": today_lessons,
        "nb_stats": nb_stats,
        "contract_stats": contract_stats,
    }


# ============================================
# STUDENTS (read-only)
# ============================================

@router.get("/students")
async def mobile_dean_students(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get students list (read-only)."""
    query = select(Student).where(Student.is_active == True)

    if search:
        query = query.where(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%"),
            )
        )
    if group_id:
        query = query.where(Student.group_id == group_id)
    if faculty:
        fac_groups = await db.execute(
            select(Group.id).where(
                and_(Group.is_active == True, Group.faculty == faculty)
            )
        )
        fac_ids = [r[0] for r in fac_groups.all()]
        query = query.where(Student.group_id.in_(fac_ids)) if fac_ids else query.where(Student.id == -1)
    if course_year:
        cy_groups = await db.execute(
            select(Group.id).where(
                and_(Group.is_active == True, Group.course_year == course_year)
            )
        )
        cy_ids = [r[0] for r in cy_groups.all()]
        query = query.where(Student.group_id.in_(cy_ids)) if cy_ids else query.where(Student.id == -1)

    total = (
        await db.execute(select(func.count()).select_from(query.subquery()))
    ).scalar() or 0

    query = (
        query.options(joinedload(Student.group))
        .order_by(Student.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    students = result.scalars().unique().all()

    items = []
    for s in students:
        items.append(
            {
                "id": s.id,
                "name": s.name,
                "student_id": s.student_id,
                "group_id": s.group_id,
                "group_name": s.group.name if s.group else "",
                "phone": s.phone,
                "is_active": s.is_active,
                "contract_amount": float(getattr(s, "contract_amount", 0) or 0),
                "contract_paid": float(getattr(s, "contract_paid", 0) or 0),
            }
        )

    return {"items": items, "total": total, "page": page, "per_page": per_page}


# ============================================
# GROUPS
# ============================================

@router.get("/groups")
async def mobile_dean_groups(
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get groups with student counts."""
    query = (
        select(Group, func.count(Student.id).label("students_count"))
        .outerjoin(
            Student, and_(Student.group_id == Group.id, Student.is_active == True)
        )
        .where(Group.is_active == True)
    )
    if faculty:
        query = query.where(Group.faculty == faculty)
    if course_year:
        query = query.where(Group.course_year == course_year)

    query = query.group_by(Group.id).order_by(Group.name)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for g, cnt in rows:
        items.append(
            {
                "id": g.id,
                "name": g.name,
                "faculty": g.faculty,
                "course_year": g.course_year,
                "students_count": cnt or 0,
            }
        )

    return {"groups": items, "total": len(items)}


@router.get("/faculties")
async def mobile_dean_faculties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get faculties list with group/student counts."""
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
# ATTENDANCE (read-only)
# ============================================

@router.get("/attendance")
async def mobile_dean_attendance(
    date_val: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get attendance records (read-only)."""
    today = today_tashkent()

    if date_from or date_to:
        try:
            d_from = date.fromisoformat(date_from) if date_from else today
        except ValueError:
            d_from = today
        try:
            d_to = date.fromisoformat(date_to) if date_to else d_from
        except ValueError:
            d_to = d_from
        query = (
            select(Attendance)
            .join(Student, Student.id == Attendance.student_id)
            .where(Attendance.date >= d_from, Attendance.date <= d_to)
        )
    else:
        target_date = today
        if date_val:
            try:
                target_date = date.fromisoformat(date_val)
            except ValueError:
                pass
        query = (
            select(Attendance)
            .join(Student, Student.id == Attendance.student_id)
            .where(Attendance.date == target_date)
        )

    if group_id:
        query = query.where(Student.group_id == group_id)
    if status_filter:
        try:
            query = query.where(Attendance.status == AttendanceStatus(status_filter))
        except ValueError:
            pass

    total = (
        await db.execute(select(func.count()).select_from(query.subquery()))
    ).scalar() or 0

    query = query.order_by(Student.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    records = result.scalars().all()

    stats = {"total": total, "present": 0, "absent": 0, "late": 0, "excused": 0}
    items = []
    for a in records:
        s_val = a.status.value
        if s_val == "present":
            stats["present"] += 1
        elif s_val == "absent":
            stats["absent"] += 1
        elif s_val == "late":
            stats["late"] += 1
        elif s_val == "excused":
            stats["excused"] += 1

        items.append(
            {
                "id": a.id,
                "student_id": a.student_id,
                "student_name": a.student_name,
                "group_name": getattr(a, "group_name", ""),
                "status": s_val,
                "subject": a.subject,
                "lesson_number": a.lesson_number,
                "date": str(a.date),
                "note": getattr(a, "note", ""),
            }
        )

    return {"items": items, "total": total, "stats": stats, "page": page}


# ============================================
# SCHEDULE (read-only)
# ============================================

@router.get("/schedule")
async def mobile_dean_schedule(
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    teacher: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get schedule (read-only)."""
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
                "group_id": s.group_id,
                "group_name": s.group.name if s.group else None,
                "teacher_name": s.teacher_name,
                "day_of_week": s.day_of_week.value if s.day_of_week else None,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
                "is_cancelled": s.is_cancelled,
            }
        )

    return {"items": items, "total": total, "page": page}


# ============================================
# CONTRACTS (read-only)
# ============================================

@router.get("/contracts")
async def mobile_dean_contracts(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    has_debt: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get contracts (read-only)."""
    try:
        from app.models.contract import Contract

        query = (
            select(Contract)
            .join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
            .options(joinedload(Contract.student).joinedload(Student.group))
        )

        if search:
            query = query.where(
                or_(
                    Student.name.ilike(f"%{search}%"),
                    Student.student_id.ilike(f"%{search}%"),
                )
            )
        if group_id:
            query = query.where(Student.group_id == group_id)
        if faculty:
            query = query.where(Group.faculty == faculty)
        if has_debt is True:
            query = query.where(Contract.total_paid < Contract.contract_amount)
        elif has_debt is False:
            query = query.where(Contract.total_paid >= Contract.contract_amount)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        query = query.order_by(Student.name).offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        contracts = result.unique().scalars().all()

        items = []
        for c in contracts:
            debt = float((c.contract_amount or 0) - (c.total_paid or 0))
            items.append(
                {
                    "id": c.id,
                    "student_name": c.student_name,
                    "group_name": getattr(c, "group_name", ""),
                    "direction": c.direction or "",
                    "contract_amount": float(c.contract_amount or 0),
                    "paid_amount": float(c.total_paid or 0),
                    "debt": debt,
                    "is_paid": debt <= 0,
                }
            )

        return {"items": items, "total": total, "page": page}

    except ImportError:
        return {"items": [], "total": 0}


# ============================================
# NB PERMITS (read-only)
# ============================================

@router.get("/nb-permits")
async def mobile_dean_nb_permits(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get NB permits (read-only)."""
    try:
        from app.models.nb_permit import NBPermit

        query = select(NBPermit).options(joinedload(NBPermit.student))

        if search:
            query = (
                query.join(Student, Student.id == NBPermit.student_id, isouter=True)
                .where(
                    or_(
                        NBPermit.permit_code.ilike(f"%{search}%"),
                        NBPermit.subject_name.ilike(f"%{search}%"),
                        Student.name.ilike(f"%{search}%"),
                    )
                )
            )
        if status_filter:
            query = query.where(NBPermit.status == status_filter)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        query = (
            query.order_by(NBPermit.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await db.execute(query)
        permits = result.unique().scalars().all()

        items = []
        for p in permits:
            items.append(
                {
                    "id": p.id,
                    "permit_code": p.permit_code,
                    "student_name": p.student.name if p.student else "",
                    "subject_name": p.subject_name,
                    "teacher_name": getattr(p, "teacher_name", ""),
                    "nb_type": getattr(p, "nb_type", ""),
                    "status": p.status if isinstance(p.status, str) else p.status.value,
                    "issue_date": str(p.issue_date) if p.issue_date else None,
                    "expiry_date": str(p.expiry_date) if getattr(p, "expiry_date", None) else None,
                }
            )

        return {"items": items, "total": total, "page": page}

    except ImportError:
        return {"items": [], "total": 0}


# ============================================
# WORKLOAD (read-only)
# ============================================

@router.get("/workload")
async def mobile_dean_workload(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_dean),
):
    """Get teacher workload (read-only)."""
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
