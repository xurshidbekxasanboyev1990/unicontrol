"""
UniControl - Mobile Teacher Panel
==================================
Teacher mobile endpoints: dashboard, schedule, groups,
attendance marking, attendance summary, profile, workload.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional, List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct, case
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.schedule import Schedule, WeekDay
from app.models.group import Group
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.teacher_workload import TeacherWorkload
from app.core.dependencies import get_current_active_user
from app.core.security import get_password_hash, verify_password
from app.config import today_tashkent, TASHKENT_TZ

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_mobile_teacher(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require teacher role for mobile."""
    if current_user.role not in [
        UserRole.TEACHER,
        UserRole.ACADEMIC_AFFAIRS,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ]:
        raise HTTPException(status_code=403, detail="O'qituvchi ruxsati kerak")
    return current_user


# ============================================
# Schemas
# ============================================

class MobileAttendanceMarkItem(BaseModel):
    student_id: int
    status: str = "present"
    note: Optional[str] = None
    late_minutes: int = 0


class MobileAttendanceBatch(BaseModel):
    group_id: int
    date: str  # YYYY-MM-DD
    subject: Optional[str] = None
    lesson_number: Optional[int] = None
    attendances: List[MobileAttendanceMarkItem]


class MobileChangePassword(BaseModel):
    current_password: str
    new_password: str


class MobileProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


# ============================================
# Helpers
# ============================================

def _get_today_weekday() -> WeekDay:
    """Get current weekday as WeekDay enum."""
    day_map = {
        0: WeekDay.MONDAY,
        1: WeekDay.TUESDAY,
        2: WeekDay.WEDNESDAY,
        3: WeekDay.THURSDAY,
        4: WeekDay.FRIDAY,
        5: WeekDay.SATURDAY,
        6: WeekDay.SUNDAY,
    }
    return day_map[today_tashkent().weekday()]


async def _get_teacher_group_ids(db: AsyncSession, teacher_id: int) -> List[int]:
    """Get all group IDs assigned to this teacher via schedules."""
    result = await db.execute(
        select(distinct(Schedule.group_id)).where(
            and_(Schedule.teacher_id == teacher_id, Schedule.is_active == True)
        )
    )
    return [row[0] for row in result.all()]


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def mobile_teacher_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Teacher mobile dashboard — today's lessons, groups, attendance rate."""
    teacher_id = current_user.id
    today = today_tashkent()
    today_weekday = _get_today_weekday()

    group_ids = await _get_teacher_group_ids(db, teacher_id)

    # Total students
    total_students = 0
    if group_ids:
        result = await db.execute(
            select(func.count(Student.id)).where(
                and_(Student.group_id.in_(group_ids), Student.is_active == True)
            )
        )
        total_students = result.scalar() or 0

    # Today's lessons
    today_lessons_result = await db.execute(
        select(Schedule)
        .options(joinedload(Schedule.group))
        .where(
            and_(
                Schedule.teacher_id == teacher_id,
                Schedule.is_active == True,
                Schedule.is_cancelled == False,
                Schedule.day_of_week == today_weekday,
            )
        )
        .order_by(Schedule.start_time)
    )
    today_lessons = today_lessons_result.unique().scalars().all()

    # Weekly lessons count
    weekly_result = await db.execute(
        select(func.count(Schedule.id)).where(
            and_(
                Schedule.teacher_id == teacher_id,
                Schedule.is_active == True,
                Schedule.is_cancelled == False,
            )
        )
    )
    weekly_lessons = weekly_result.scalar() or 0

    # Today's attendance rate
    today_attendance_rate = 0.0
    if group_ids:
        total_att = await db.execute(
            select(func.count(Attendance.id))
            .join(Student, Student.id == Attendance.student_id)
            .where(and_(Attendance.date == today, Student.group_id.in_(group_ids)))
        )
        present_att = await db.execute(
            select(func.count(Attendance.id))
            .join(Student, Student.id == Attendance.student_id)
            .where(
                and_(
                    Attendance.date == today,
                    Student.group_id.in_(group_ids),
                    Attendance.status.in_(
                        [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                    ),
                )
            )
        )
        total_count = total_att.scalar() or 0
        present_count = present_att.scalar() or 0
        if total_count > 0:
            today_attendance_rate = round(present_count / total_count * 100, 1)

    # Format today schedule
    today_schedule = []
    for s in today_lessons:
        today_schedule.append(
            {
                "id": s.id,
                "subject": s.subject,
                "group_id": s.group_id,
                "group_name": s.group_name,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
            }
        )

    return {
        "role": "teacher",
        "total_groups": len(group_ids),
        "total_students": total_students,
        "today_lessons": len(today_lessons),
        "weekly_lessons": weekly_lessons,
        "today_attendance_rate": today_attendance_rate,
        "today_schedule": today_schedule,
    }


# ============================================
# SCHEDULE
# ============================================

@router.get("/schedule")
async def mobile_teacher_schedule(
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get teacher's full weekly schedule."""
    query = (
        select(Schedule)
        .options(joinedload(Schedule.group))
        .where(
            and_(Schedule.teacher_id == current_user.id, Schedule.is_active == True)
        )
    )
    if group_id:
        query = query.where(Schedule.group_id == group_id)

    query = query.order_by(Schedule.day_of_week, Schedule.start_time)
    result = await db.execute(query)
    schedules = result.unique().scalars().all()

    items = []
    for s in schedules:
        items.append(
            {
                "id": s.id,
                "subject": s.subject,
                "group_id": s.group_id,
                "group_name": s.group_name,
                "day_of_week": s.day_of_week.value if s.day_of_week else None,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "building": s.building,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
                "is_cancelled": s.is_cancelled,
            }
        )

    return {"schedule": items, "total": len(items)}


@router.get("/schedule/today")
async def mobile_teacher_schedule_today(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get today's schedule for teacher."""
    today = today_tashkent()
    today_weekday = _get_today_weekday()

    result = await db.execute(
        select(Schedule)
        .options(joinedload(Schedule.group))
        .where(
            and_(
                Schedule.teacher_id == current_user.id,
                Schedule.is_active == True,
                Schedule.is_cancelled == False,
                Schedule.day_of_week == today_weekday,
            )
        )
        .order_by(Schedule.start_time)
    )
    schedules = result.unique().scalars().all()

    return {
        "date": str(today),
        "day": today_weekday.value,
        "classes": [
            {
                "id": s.id,
                "subject": s.subject,
                "group_id": s.group_id,
                "group_name": s.group_name,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "room": s.room,
                "lesson_number": s.lesson_number,
                "week_type": s.week_type.value if s.week_type else "all",
            }
            for s in schedules
        ],
    }


# ============================================
# GROUPS
# ============================================

@router.get("/groups")
async def mobile_teacher_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get groups assigned to this teacher."""
    teacher_id = current_user.id
    group_ids = await _get_teacher_group_ids(db, teacher_id)

    if not group_ids:
        return {"groups": [], "total": 0}

    groups_result = await db.execute(
        select(Group).where(Group.id.in_(group_ids)).order_by(Group.name)
    )
    groups = groups_result.scalars().all()

    items = []
    for g in groups:
        student_count = await db.execute(
            select(func.count(Student.id)).where(
                and_(Student.group_id == g.id, Student.is_active == True)
            )
        )
        subjects_result = await db.execute(
            select(distinct(Schedule.subject)).where(
                and_(
                    Schedule.teacher_id == teacher_id,
                    Schedule.group_id == g.id,
                    Schedule.is_active == True,
                )
            )
        )
        subjects = [row[0] for row in subjects_result.all()]

        items.append(
            {
                "id": g.id,
                "name": g.name,
                "faculty": g.faculty,
                "course_year": g.course_year,
                "students_count": student_count.scalar() or 0,
                "subjects": subjects,
            }
        )

    return {"groups": items, "total": len(items)}


@router.get("/groups/{group_id}/students")
async def mobile_teacher_group_students(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get students in a group (teacher must be assigned)."""
    teacher_id = current_user.id
    group_ids = await _get_teacher_group_ids(db, teacher_id)

    if group_id not in group_ids:
        raise HTTPException(status_code=403, detail="Bu guruhga ruxsat yo'q")

    students_result = await db.execute(
        select(Student)
        .where(and_(Student.group_id == group_id, Student.is_active == True))
        .order_by(Student.name)
    )
    students = students_result.scalars().all()

    today = today_tashkent()
    thirty_days_ago = today - timedelta(days=30)

    items = []
    for s in students:
        total_att = await db.execute(
            select(func.count(Attendance.id)).where(
                and_(
                    Attendance.student_id == s.id,
                    Attendance.date >= thirty_days_ago,
                    Attendance.date <= today,
                )
            )
        )
        present_att = await db.execute(
            select(func.count(Attendance.id)).where(
                and_(
                    Attendance.student_id == s.id,
                    Attendance.date >= thirty_days_ago,
                    Attendance.date <= today,
                    Attendance.status.in_(
                        [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                    ),
                )
            )
        )
        t = total_att.scalar() or 0
        p = present_att.scalar() or 0
        rate = round(p / t * 100, 1) if t > 0 else None

        items.append(
            {
                "id": s.id,
                "name": s.name,
                "full_name": getattr(s, "full_name", s.name),
                "hemis_id": s.hemis_id,
                "student_id": s.student_id,
                "phone": s.phone,
                "is_active": s.is_active,
                "attendance_rate": rate,
            }
        )

    return {"students": items, "total": len(items)}


# ============================================
# ATTENDANCE — view
# ============================================

@router.get("/attendance")
async def mobile_teacher_attendance(
    group_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get attendance history for teacher's groups."""
    teacher_id = current_user.id
    group_ids = await _get_teacher_group_ids(db, teacher_id)

    if not group_ids:
        return {"items": [], "total": 0}

    if group_id and group_id not in group_ids:
        raise HTTPException(status_code=403, detail="Bu guruhga ruxsat yo'q")

    target_groups = [group_id] if group_id else group_ids
    today = today_tashkent()

    try:
        d_from = date.fromisoformat(date_from) if date_from else today
        d_to = date.fromisoformat(date_to) if date_to else today
    except ValueError:
        d_from = today
        d_to = today

    result = await db.execute(
        select(Attendance)
        .join(Student, Student.id == Attendance.student_id)
        .where(
            and_(
                Student.group_id.in_(target_groups),
                Attendance.date >= d_from,
                Attendance.date <= d_to,
            )
        )
        .order_by(Attendance.date.desc(), Student.name)
    )
    records = result.scalars().all()

    items = []
    for a in records:
        items.append(
            {
                "id": a.id,
                "student_id": a.student_id,
                "student_name": a.student_name,
                "date": str(a.date),
                "status": a.status.value,
                "subject": a.subject,
                "lesson_number": a.lesson_number,
                "note": getattr(a, "note", "") or "",
                "late_minutes": a.late_minutes,
            }
        )

    # Stats
    stats = {
        "total": len(items),
        "present": sum(1 for i in items if i["status"] == "present"),
        "absent": sum(1 for i in items if i["status"] == "absent"),
        "late": sum(1 for i in items if i["status"] == "late"),
        "excused": sum(1 for i in items if i["status"] == "excused"),
    }

    return {"items": items, "total": len(items), "stats": stats}


# ============================================
# ATTENDANCE — mark (POST)
# ============================================

@router.post("/attendance")
async def mobile_teacher_mark_attendance(
    data: MobileAttendanceBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Mark attendance for a group (batch) from mobile."""
    teacher_id = current_user.id
    group_ids = await _get_teacher_group_ids(db, teacher_id)

    if data.group_id not in group_ids:
        raise HTTPException(status_code=403, detail="Bu guruhga ruxsat yo'q")

    try:
        att_date = date.fromisoformat(data.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Noto'g'ri sana formati (YYYY-MM-DD)")

    created = 0
    updated = 0

    for item in data.attendances:
        existing = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == item.student_id,
                    Attendance.date == att_date,
                    or_(
                        Attendance.lesson_number == data.lesson_number,
                        and_(
                            Attendance.lesson_number.is_(None),
                            data.lesson_number is None,
                        ),
                    ),
                )
            )
        )
        existing_att = existing.scalar_one_or_none()

        try:
            att_status = AttendanceStatus(item.status)
        except ValueError:
            att_status = AttendanceStatus.ABSENT

        if existing_att:
            existing_att.status = att_status
            existing_att.note = item.note
            existing_att.late_minutes = item.late_minutes
            existing_att.recorded_by = teacher_id
            existing_att.subject = data.subject
            updated += 1
        else:
            new_att = Attendance(
                student_id=item.student_id,
                date=att_date,
                status=att_status,
                subject=data.subject,
                lesson_number=data.lesson_number,
                note=item.note,
                late_minutes=item.late_minutes,
                recorded_by=teacher_id,
            )
            db.add(new_att)
            created += 1

    await db.commit()

    return {
        "success": True,
        "message": f"Davomat saqlandi: {created} yangi, {updated} yangilandi",
        "created": created,
        "updated": updated,
    }


# ============================================
# ATTENDANCE SUMMARY
# ============================================

@router.get("/attendance/summary")
async def mobile_teacher_attendance_summary(
    group_id: int = Query(...),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get attendance summary for a group — per-student stats."""
    teacher_id = current_user.id
    group_ids = await _get_teacher_group_ids(db, teacher_id)

    if group_id not in group_ids:
        raise HTTPException(status_code=403, detail="Bu guruhga ruxsat yo'q")

    today = today_tashkent()
    try:
        d_from = date.fromisoformat(date_from) if date_from else today - timedelta(days=30)
        d_to = date.fromisoformat(date_to) if date_to else today
    except ValueError:
        d_from = today - timedelta(days=30)
        d_to = today

    students_result = await db.execute(
        select(Student)
        .where(and_(Student.group_id == group_id, Student.is_active == True))
        .order_by(Student.name)
    )
    students = students_result.scalars().all()

    summary = []
    for s in students:
        result = await db.execute(
            select(
                func.count(Attendance.id).label("total"),
                func.count(
                    case((Attendance.status == AttendanceStatus.PRESENT, 1))
                ).label("present"),
                func.count(
                    case((Attendance.status == AttendanceStatus.ABSENT, 1))
                ).label("absent"),
                func.count(
                    case((Attendance.status == AttendanceStatus.LATE, 1))
                ).label("late"),
                func.count(
                    case((Attendance.status == AttendanceStatus.EXCUSED, 1))
                ).label("excused"),
            ).where(
                and_(
                    Attendance.student_id == s.id,
                    Attendance.date >= d_from,
                    Attendance.date <= d_to,
                )
            )
        )
        row = result.one()
        total = row.total or 0
        present = row.present or 0
        late = row.late or 0
        rate = round((present + late) / total * 100, 1) if total > 0 else 0

        summary.append(
            {
                "student_id": s.id,
                "student_name": s.name,
                "hemis_id": s.hemis_id,
                "total": total,
                "present": present,
                "absent": row.absent or 0,
                "late": late,
                "excused": row.excused or 0,
                "rate": rate,
            }
        )

    return {
        "group_id": group_id,
        "date_from": str(d_from),
        "date_to": str(d_to),
        "students": summary,
    }


# ============================================
# PROFILE
# ============================================

@router.get("/profile")
async def mobile_teacher_profile(
    current_user: User = Depends(require_mobile_teacher),
):
    """Get teacher profile."""
    return {
        "id": current_user.id,
        "login": current_user.login,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar": current_user.avatar,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": str(current_user.created_at) if current_user.created_at else None,
    }


@router.put("/profile")
async def mobile_teacher_update_profile(
    data: MobileProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Update teacher profile."""
    if data.name is not None:
        current_user.name = data.name
    if data.phone is not None:
        current_user.phone = data.phone
    if data.email is not None:
        current_user.email = data.email

    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "message": "Profil yangilandi",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
        },
    }


@router.post("/change-password")
async def mobile_teacher_change_password(
    data: MobileChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Change teacher password."""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Joriy parol noto'g'ri")

    current_user.password_hash = get_password_hash(data.new_password)
    if hasattr(current_user, "plain_password"):
        current_user.plain_password = data.new_password

    await db.commit()
    return {"success": True, "message": "Parol muvaffaqiyatli o'zgartirildi"}


# ============================================
# WORKLOAD
# ============================================

@router.get("/workload")
async def mobile_teacher_workload(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_teacher),
):
    """Get current teacher's own workload by name matching."""
    teacher_name = current_user.name
    if not teacher_name:
        return {"items": [], "total": 0, "teacher_name": ""}

    name_parts = teacher_name.strip().split()
    query = select(TeacherWorkload).where(TeacherWorkload.is_active == True)

    conditions = []
    for part in name_parts:
        if len(part) > 2:
            conditions.append(TeacherWorkload.teacher_name.ilike(f"%{part}%"))

    if conditions:
        query = query.where(and_(*conditions))
    else:
        query = query.where(TeacherWorkload.teacher_name.ilike(f"%{teacher_name}%"))

    query = query.order_by(
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
    matched_name = ""
    for w in workloads:
        if not matched_name:
            matched_name = w.teacher_name
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

    return {
        "items": items,
        "total": len(items),
        "teacher_name": matched_name,
    }
