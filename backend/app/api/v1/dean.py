"""
UniControl - Dean Panel API Routes (Dekanat)
=============================================
Read-only endpoints for dean panel:
- Dashboard statistics
- Students kontingent (read-only)
- Attendance viewing + Excel import
- Schedule viewing
- Workload viewing
- Contract info (read-only)
- NB Permits viewing (read-only)

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional, List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
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
from app.config import today_tashkent, TASHKENT_TZ
from pydantic import BaseModel

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_dean(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require dean or higher role."""
    if current_user.role not in [UserRole.DEAN, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Dekanat ruxsati kerak")
    return current_user


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def dean_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get dean dashboard statistics."""
    today = today_tashkent()

    # Combined query: total students + total groups in parallel
    import asyncio
    
    async def get_counts():
        total_students_result = await db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
        total_groups_result = await db.execute(
            select(func.count(Group.id)).where(Group.is_active == True)
        )
        return total_students_result.scalar() or 0, total_groups_result.scalar() or 0

    total_students, total_groups = await get_counts()

    # Combined attendance query: present, absent, total in ONE query
    attendance_stats = await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.count(Attendance.id).filter(
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
            ).label("present"),
            func.count(Attendance.id).filter(
                Attendance.status == AttendanceStatus.ABSENT
            ).label("absent"),
        ).where(Attendance.date == today)
    )
    att_row = attendance_stats.one()
    total_today = att_row.total or 0
    present_count = att_row.present or 0
    absent_count = att_row.absent or 0

    attendance_rate = round(present_count / total_today * 100, 1) if total_today > 0 else 0

    # Today lessons count
    from app.models.schedule import WeekDay
    day_map = {0: WeekDay.MONDAY, 1: WeekDay.TUESDAY, 2: WeekDay.WEDNESDAY,
               3: WeekDay.THURSDAY, 4: WeekDay.FRIDAY, 5: WeekDay.SATURDAY, 6: WeekDay.SUNDAY}
    today_weekday = day_map[today.weekday()]

    today_lessons_result = await db.execute(
        select(func.count(Schedule.id)).where(
            and_(
                Schedule.is_active == True,
                Schedule.is_cancelled == False,
                Schedule.day_of_week == today_weekday
            )
        )
    )
    today_lessons = today_lessons_result.scalar() or 0

    # NB permits stats (combined single query)
    nb_stats = {"total": 0, "active": 0, "approved": 0}
    try:
        from app.models.nb_permit import NBPermit
        nb_result = await db.execute(
            select(
                func.count(NBPermit.id).label("total"),
                func.count(NBPermit.id).filter(
                    NBPermit.status.in_(["issued", "pending", "in_progress"])
                ).label("active"),
                func.count(NBPermit.id).filter(
                    NBPermit.status == "approved"
                ).label("approved"),
            )
        )
        nb_row = nb_result.one()
        nb_stats = {"total": nb_row.total or 0, "active": nb_row.active or 0, "approved": nb_row.approved or 0}
    except Exception:
        pass

    # Contract stats (try)
    contract_stats = {"total": 0, "paid": 0, "debt": 0}
    try:
        from app.models.contract import Contract
        contract_result = await db.execute(
            select(
                func.count(Contract.id),
                func.coalesce(func.sum(Contract.total_paid), 0),
                func.coalesce(func.sum(Contract.contract_amount), 0)
            )
        )
        row = contract_result.one()
        contract_stats["total"] = row[0] or 0
        contract_stats["paid"] = float(row[1] or 0)
        contract_stats["debt"] = float((row[2] or 0) - (row[1] or 0))
    except Exception:
        pass

    return {
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
# STUDENTS (Read-only)
# ============================================

@router.get("/students")
async def dean_students(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    page: int = 1,
    per_page: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get students list (read-only)."""
    query = select(Student).where(Student.is_active == True)

    if search:
        query = query.where(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%"),
                Student.hemis_id.ilike(f"%{search}%")
            )
        )

    if group_id:
        query = query.where(Student.group_id == group_id)

    # Filter by faculty through group
    if faculty:
        faculty_groups = await db.execute(
            select(Group.id).where(and_(Group.is_active == True, Group.faculty == faculty))
        )
        faculty_group_ids = [r[0] for r in faculty_groups.all()]
        if faculty_group_ids:
            query = query.where(Student.group_id.in_(faculty_group_ids))
        else:
            query = query.where(Student.id == -1)  # No results

    # Filter by course year through group
    if course_year:
        course_groups = await db.execute(
            select(Group.id).where(and_(Group.is_active == True, Group.course_year == course_year))
        )
        course_group_ids = [r[0] for r in course_groups.all()]
        if course_group_ids:
            query = query.where(Student.group_id.in_(course_group_ids))
        else:
            query = query.where(Student.id == -1)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * per_page
    query = query.order_by(Student.name).offset(offset).limit(per_page)

    # Eager load group relationship to avoid N+1
    from sqlalchemy.orm import joinedload
    query = query.options(joinedload(Student.group))
    result = await db.execute(query)
    students = result.scalars().unique().all()

    items = []
    for s in students:
        group_name = s.group.name if s.group else ""

        items.append({
            "id": s.id,
            "name": s.name,
            "student_id": s.student_id,
            "hemis_id": s.hemis_id,
            "group_id": s.group_id,
            "group_name": group_name,
            "phone": s.phone,
            "email": s.email,
            "passport": getattr(s, 'passport', None),
            "address": getattr(s, 'address', None),
            "is_active": s.is_active,
            "contract_amount": float(getattr(s, 'contract_amount', 0) or 0),
            "contract_paid": float(getattr(s, 'contract_paid', 0) or 0),
        })

    return {"items": items, "total": total, "page": page, "per_page": per_page}


# ============================================
# GROUPS
# ============================================

@router.get("/faculties")
async def dean_faculties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get distinct faculties list."""
    result = await db.execute(
        select(distinct(Group.faculty))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != ""))
        .order_by(Group.faculty)
    )
    faculties = [row[0] for row in result.all() if row[0]]
    return {"faculties": faculties}


@router.get("/faculties-tree")
async def dean_faculties_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """
    Get flat faculty list with groups for kontingent.
    Uses REAL data from DB (groups.faculty) — no hardcoded mappings.
    Each faculty = one direction from imported Excel.
    """
    result = await db.execute(
        select(
            Group.id,
            Group.name,
            Group.faculty,
            Group.course_year,
            func.count(Student.id).label('students_count')
        )
        .outerjoin(Student, and_(Student.group_id == Group.id, Student.is_active == True))
        .where(Group.is_active == True)
        .group_by(Group.id, Group.name, Group.faculty, Group.course_year)
        .order_by(Group.faculty, Group.name)
    )
    rows = result.all()

    # Build faculty → groups mapping from actual DB data
    faculty_map = {}
    for row in rows:
        faculty_name = row.faculty or "Boshqa"
        if faculty_name not in faculty_map:
            faculty_map[faculty_name] = []
        faculty_map[faculty_name].append({
            "id": row.id,
            "name": row.name,
            "course_year": row.course_year,
            "students_count": row.students_count or 0,
        })

    # Each faculty is a flat entry (no super-faculty grouping)
    faculties = []
    for faculty_name in sorted(faculty_map.keys()):
        groups = faculty_map[faculty_name]
        faculties.append({
            "name": faculty_name,
            "directions": [{"name": faculty_name, "groups": sorted(groups, key=lambda g: g["name"]), "groups_count": len(groups), "students_count": sum(g["students_count"] for g in groups)}],
            "directions_count": 1,
            "groups_count": len(groups),
            "students_count": sum(g["students_count"] for g in groups),
        })

    return {
        "faculties": faculties,
        "total_faculties": len(faculties),
        "total_directions": len(faculties),
        "total_groups": sum(f["groups_count"] for f in faculties),
    }


@router.get("/groups")
async def dean_groups(
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get all groups with optional filters."""
    # Single query with LEFT JOIN + GROUP BY (no N+1)
    query = (
        select(
            Group,
            func.count(Student.id).label("students_count")
        )
        .outerjoin(
            Student,
            and_(Student.group_id == Group.id, Student.is_active == True)
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
        items.append({
            "id": g.id,
            "name": g.name,
            "faculty": g.faculty,
            "course_year": g.course_year,
            "students_count": cnt or 0,
        })

    return {"items": items, "total": len(items)}


# ============================================
# ATTENDANCE (Read-only + Excel import)
# ============================================

@router.get("/attendance")
async def dean_attendance(
    date_val: Optional[str] = None,
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get attendance records (read-only)."""
    today = today_tashkent()
    target_date = today

    if date_val:
        try:
            target_date = date.fromisoformat(date_val)
        except ValueError:
            target_date = today

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

    query = query.order_by(Student.name)
    result = await db.execute(query)
    records = result.scalars().all()

    # Stats
    stats = {"total": 0, "present": 0, "absent": 0, "late": 0, "excused": 0}
    items = []
    for a in records:
        stats["total"] += 1
        if a.status == AttendanceStatus.PRESENT:
            stats["present"] += 1
        elif a.status == AttendanceStatus.ABSENT:
            stats["absent"] += 1
        elif a.status == AttendanceStatus.LATE:
            stats["late"] += 1
        elif a.status == AttendanceStatus.EXCUSED:
            stats["excused"] += 1

        items.append({
            "id": a.id,
            "student_id": a.student_id,
            "student_name": a.student_name,
            "group_name": getattr(a, 'group_name', ''),
            "subject": a.subject,
            "lesson_number": a.lesson_number,
            "status": a.status.value,
            "check_in_time": a.check_in_time.strftime("%H:%M") if a.check_in_time else None,
            "note": getattr(a, 'note', ''),
        })

    return {"items": items, "stats": stats}


@router.get("/attendance/export")
async def dean_attendance_export(
    date_val: Optional[str] = None,
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Export attendance to print-ready Excel."""
    from fastapi.responses import StreamingResponse
    from app.services.excel_service import ExcelService

    today = today_tashkent()
    target_date = today
    if date_val:
        try:
            target_date = date.fromisoformat(date_val)
        except ValueError:
            target_date = today

    service = ExcelService(db)
    file_data = await service.export_attendance_printable(
        group_id=group_id,
        date_from=target_date,
        date_to=target_date,
        status_filter=status_filter,
    )

    # Build filename
    fname_parts = ["davomat", target_date.strftime("%d_%m_%Y")]
    if group_id:
        fname_parts.insert(1, f"guruh_{group_id}")
    filename = "_".join(fname_parts) + ".xlsx"

    return StreamingResponse(
        file_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/attendance/import")
async def dean_attendance_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Import attendance from Excel file.
    
    Expected columns: student_id (or hemis_id), date (YYYY-MM-DD), status (present/absent/late/excused), subject, lesson_number
    """
    import io
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl kutubxonasi o'rnatilmagan")

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Faqat Excel (.xlsx) fayl yuklash mumkin")

    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="Fayl bo'sh yoki sarlavha qatori topilmadi")

    # Find column indices from header
    header = [str(c).strip().lower() if c else '' for c in rows[0]]

    # Map column names
    col_map = {}
    for i, h in enumerate(header):
        if h in ('student_id', 'talaba_id', 'hemis_id', 'id'):
            col_map['student_id'] = i
        elif h in ('date', 'sana', 'kun'):
            col_map['date'] = i
        elif h in ('status', 'holat', 'davomat'):
            col_map['status'] = i
        elif h in ('subject', 'fan', 'dars'):
            col_map['subject'] = i
        elif h in ('lesson', 'lesson_number', 'dars_raqami', 'para'):
            col_map['lesson_number'] = i

    if 'student_id' not in col_map or 'status' not in col_map:
        raise HTTPException(
            status_code=400,
            detail="Excel faylda 'student_id' va 'status' ustunlari topilmadi. Ustun nomlari: " + ", ".join(header)
        )

    created = 0
    updated = 0
    errors = []

    status_map = {
        'kelgan': 'present', 'present': 'present', 'bor': 'present', '+': 'present', '1': 'present',
        'kelmagan': 'absent', 'absent': 'absent', 'yoq': 'absent', '-': 'absent', '0': 'absent',
        'kechikkan': 'late', 'late': 'late', 'kech': 'late',
        'sababli': 'excused', 'excused': 'excused', 'uzr': 'excused',
    }

    for row_idx, row in enumerate(rows[1:], start=2):
        try:
            student_id_val = str(row[col_map['student_id']]).strip() if row[col_map['student_id']] else None
            if not student_id_val:
                continue

            # Find student
            student = None
            s_result = await db.execute(
                select(Student).where(
                    or_(
                        Student.student_id == student_id_val,
                        Student.hemis_id == student_id_val,
                    )
                )
            )
            student = s_result.scalar_one_or_none()
            if not student:
                # Try as numeric id
                try:
                    s_result2 = await db.execute(
                        select(Student).where(Student.id == int(student_id_val))
                    )
                    student = s_result2.scalar_one_or_none()
                except (ValueError, TypeError):
                    pass

            if not student:
                errors.append(f"Qator {row_idx}: Talaba topilmadi ({student_id_val})")
                continue

            # Parse date
            att_date = today_tashkent()
            if 'date' in col_map and row[col_map['date']]:
                raw_date = row[col_map['date']]
                if isinstance(raw_date, datetime):
                    att_date = raw_date.date()
                elif isinstance(raw_date, date):
                    att_date = raw_date
                else:
                    try:
                        att_date = date.fromisoformat(str(raw_date).strip())
                    except ValueError:
                        att_date = today_tashkent()

            # Parse status
            raw_status = str(row[col_map['status']]).strip().lower() if row[col_map['status']] else 'absent'
            att_status_str = status_map.get(raw_status, 'absent')
            try:
                att_status = AttendanceStatus(att_status_str)
            except ValueError:
                att_status = AttendanceStatus.ABSENT

            # Parse optional fields
            subject = None
            if 'subject' in col_map and row[col_map['subject']]:
                subject = str(row[col_map['subject']]).strip()

            lesson_number = None
            if 'lesson_number' in col_map and row[col_map['lesson_number']]:
                try:
                    lesson_number = int(row[col_map['lesson_number']])
                except (ValueError, TypeError):
                    pass

            # Check existing
            existing = await db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.student_id == student.id,
                        Attendance.date == att_date,
                        or_(
                            Attendance.lesson_number == lesson_number,
                            and_(
                                Attendance.lesson_number.is_(None),
                                lesson_number is None
                            )
                        )
                    )
                )
            )
            existing_att = existing.scalar_one_or_none()

            if existing_att:
                existing_att.status = att_status
                existing_att.subject = subject or existing_att.subject
                existing_att.recorded_by = current_user.id
                updated += 1
            else:
                new_att = Attendance(
                    student_id=student.id,
                    date=att_date,
                    status=att_status,
                    subject=subject,
                    lesson_number=lesson_number,
                    recorded_by=current_user.id,
                    student_name=student.name,
                )
                db.add(new_att)
                created += 1

        except Exception as e:
            errors.append(f"Qator {row_idx}: {str(e)}")

    await db.commit()

    return {
        "success": True,
        "message": f"Import tugallandi: {created} yangi, {updated} yangilandi",
        "created": created,
        "updated": updated,
        "errors": errors[:20],  # First 20 errors
        "total_errors": len(errors),
    }


# ============================================
# SCHEDULE (Read-only)
# ============================================

@router.get("/schedule")
async def dean_schedule(
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    teacher: Optional[str] = None,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get schedule (read-only) with pagination."""
    from sqlalchemy.orm import joinedload, load_only

    query = (
        select(Schedule)
        .options(joinedload(Schedule.group).load_only(Group.name))
        .where(Schedule.is_active == True)
    )

    if group_id:
        query = query.where(Schedule.group_id == group_id)

    # Filter by faculty through group — use subquery instead of loading all group IDs
    if faculty:
        faculty_subq = select(Group.id).where(
            and_(Group.is_active == True, Group.faculty == faculty)
        ).scalar_subquery()
        query = query.where(Schedule.group_id.in_(faculty_subq))

    # Filter by course year through group — use subquery
    if course_year:
        course_subq = select(Group.id).where(
            and_(Group.is_active == True, Group.course_year == course_year)
        ).scalar_subquery()
        query = query.where(Schedule.group_id.in_(course_subq))

    if teacher:
        query = query.where(Schedule.teacher_name.ilike(f"%{teacher}%"))

    # Total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    offset = (page - 1) * per_page
    query = query.order_by(Schedule.day_of_week, Schedule.start_time).offset(offset).limit(per_page)
    result = await db.execute(query)
    schedules = result.unique().scalars().all()

    items = []
    for s in schedules:
        items.append({
            "id": s.id,
            "subject": s.subject,
            "subject_code": s.subject_code,
            "group_id": s.group_id,
            "group_name": s.group.name if s.group else None,
            "teacher_name": s.teacher_name,
            "day_of_week": s.day_of_week.value if s.day_of_week else None,
            "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
            "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
            "time_range": s.time_range,
            "room": s.room,
            "building": s.building,
            "lesson_number": s.lesson_number,
            "week_type": s.week_type.value if s.week_type else "all",
            "schedule_type": s.schedule_type.value if s.schedule_type else None,
            "is_cancelled": s.is_cancelled,
        })

    return {"items": items, "total": total, "page": page, "per_page": per_page}


# ============================================
# WORKLOAD (Read-only)
# ============================================

@router.get("/workload")
async def dean_workload(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
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
            else_=7
        ),
        TeacherWorkload.lesson_number
    )

    result = await db.execute(query)
    workloads = result.scalars().all()

    items = []
    for w in workloads:
        items.append({
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
        })

    return {"items": items, "total": len(items)}


@router.get("/workload/departments")
async def dean_workload_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get departments list."""
    result = await db.execute(
        select(distinct(TeacherWorkload.department))
        .where(
            and_(
                TeacherWorkload.is_active == True,
                TeacherWorkload.department.isnot(None),
                TeacherWorkload.department != ""
            )
        )
        .order_by(TeacherWorkload.department)
    )
    departments = [row[0] for row in result.all() if row[0]]
    return {"departments": departments}


# ============================================
# CONTRACTS (Read-only)
# ============================================

@router.get("/contracts/filters")
async def dean_contracts_filters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get available filter options for contracts from actual DB data."""
    try:
        from app.models.contract import Contract

        # Faculties (from groups table — real imported data)
        fac_result = await db.execute(
            select(distinct(Group.faculty))
            .where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != ""))
            .order_by(Group.faculty)
        )
        faculties = [r[0] for r in fac_result.all() if r[0]]

        # Directions (from contracts table)
        dir_result = await db.execute(
            select(distinct(Contract.direction))
            .where(and_(Contract.direction.isnot(None), Contract.direction != ""))
            .order_by(Contract.direction)
        )
        directions = [r[0] for r in dir_result.all() if r[0]]

        # Education forms
        ef_result = await db.execute(
            select(distinct(Contract.education_form))
            .where(and_(Contract.education_form.isnot(None), Contract.education_form != ""))
            .order_by(Contract.education_form)
        )
        education_forms = [r[0] for r in ef_result.all() if r[0]]

        # Courses
        course_result = await db.execute(
            select(distinct(Contract.course))
            .where(Contract.course.isnot(None))
            .order_by(Contract.course)
        )
        courses = [r[0] for r in course_result.all() if r[0]]

        # Academic years
        ay_result = await db.execute(
            select(distinct(Contract.academic_year))
            .where(and_(Contract.academic_year.isnot(None), Contract.academic_year != ""))
            .order_by(Contract.academic_year)
        )
        academic_years = [r[0] for r in ay_result.all() if r[0]]

        return {
            "faculties": faculties,
            "directions": directions,
            "education_forms": education_forms,
            "courses": courses,
            "academic_years": academic_years,
        }
    except Exception:
        return {"faculties": [], "directions": [], "education_forms": [], "courses": [], "academic_years": []}


@router.get("/contracts")
async def dean_contracts(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    direction: Optional[str] = None,
    course: Optional[str] = None,
    education_form: Optional[str] = None,
    academic_year: Optional[str] = None,
    has_debt: Optional[bool] = None,
    page: int = 1,
    per_page: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get contract information (read-only) with full filters."""
    try:
        from app.models.contract import Contract

        # Base query: always join Student+Group for filtering/ordering
        query = (
            select(Contract)
            .join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
            .options(
                joinedload(Contract.student).joinedload(Student.group)
            )
        )

        # --- Filters ---
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

        if direction:
            query = query.where(Contract.direction == direction)

        if course:
            query = query.where(Contract.course == course)

        if education_form:
            query = query.where(Contract.education_form == education_form)

        if academic_year:
            query = query.where(Contract.academic_year == academic_year)

        if has_debt is True:
            query = query.where(Contract.total_paid < Contract.contract_amount)
        elif has_debt is False:
            query = query.where(Contract.total_paid >= Contract.contract_amount)

        # Count
        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        # Stats — rebuild the same filter conditions
        stats_base = (
            select(
                func.count(Contract.id),
                func.coalesce(func.sum(Contract.contract_amount), 0),
                func.coalesce(func.sum(Contract.total_paid), 0),
            )
            .join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
        )
        if search:
            stats_base = stats_base.where(
                or_(Student.name.ilike(f"%{search}%"), Student.student_id.ilike(f"%{search}%"))
            )
        if group_id:
            stats_base = stats_base.where(Student.group_id == group_id)
        if faculty:
            stats_base = stats_base.where(Group.faculty == faculty)
        if direction:
            stats_base = stats_base.where(Contract.direction == direction)
        if course:
            stats_base = stats_base.where(Contract.course == course)
        if education_form:
            stats_base = stats_base.where(Contract.education_form == education_form)
        if academic_year:
            stats_base = stats_base.where(Contract.academic_year == academic_year)
        if has_debt is True:
            stats_base = stats_base.where(Contract.total_paid < Contract.contract_amount)
        elif has_debt is False:
            stats_base = stats_base.where(Contract.total_paid >= Contract.contract_amount)

        stats_result = await db.execute(stats_base)
        sr = stats_result.one()

        total_amount = float(sr[1] or 0)
        total_paid_val = float(sr[2] or 0)
        stats = {
            "total": sr[0] or 0,
            "paid": 0,
            "unpaid": 0,
            "total_contract_amount": total_amount,
            "total_paid": total_paid_val,
            "total_debt": total_amount - total_paid_val,
            "payment_percentage": round(total_paid_val / max(total_amount, 1) * 100, 1),
        }

        # Paid/unpaid counts
        paid_count_q = (
            select(func.count(Contract.id))
            .join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
            .where(Contract.total_paid >= Contract.contract_amount)
        )
        if group_id:
            paid_count_q = paid_count_q.where(Student.group_id == group_id)
        if faculty:
            paid_count_q = paid_count_q.where(Group.faculty == faculty)
        if direction:
            paid_count_q = paid_count_q.where(Contract.direction == direction)
        if course:
            paid_count_q = paid_count_q.where(Contract.course == course)
        if education_form:
            paid_count_q = paid_count_q.where(Contract.education_form == education_form)
        if academic_year:
            paid_count_q = paid_count_q.where(Contract.academic_year == academic_year)

        paid_count = (await db.execute(paid_count_q)).scalar() or 0
        stats["paid"] = paid_count
        stats["unpaid"] = (sr[0] or 0) - paid_count

        # Paginate
        offset = (page - 1) * per_page
        query = query.order_by(Student.name).offset(offset).limit(per_page)
        result = await db.execute(query)
        contracts = result.unique().scalars().all()

        items = []
        for c in contracts:
            debt = float((c.contract_amount or 0) - (c.total_paid or 0))
            items.append({
                "id": c.id,
                "student_name": c.student_name,
                "student_id_number": getattr(c, 'student_jshshir', '') or getattr(c, 'student_id_number', ''),
                "group_name": getattr(c, 'group_name', ''),
                "direction": c.direction or '',
                "course": c.course or '',
                "education_form": c.education_form or '',
                "contract_amount": float(c.contract_amount or 0),
                "paid_amount": float(c.total_paid or 0),
                "debt": debt,
                "is_paid": debt <= 0,
                "academic_year": c.academic_year,
                "grant_percentage": float(c.grant_percentage or 0),
            })

        return {"items": items, "total": total, "stats": stats}

    except ImportError:
        return {"items": [], "total": 0, "stats": {}}


# ============================================
# NB PERMITS (Read-only)
# ============================================

@router.get("/nb-permits")
async def dean_nb_permits(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_dean)
):
    """Get NB permits (read-only)."""
    try:
        from app.models.nb_permit import NBPermit

        query = select(NBPermit)

        if search:
            query = query.where(
                or_(
                    NBPermit.permit_code.ilike(f"%{search}%"),
                    NBPermit.subject_name.ilike(f"%{search}%"),
                    NBPermit.student_name.ilike(f"%{search}%"),
                )
            )

        if status_filter:
            query = query.where(NBPermit.status == status_filter)

        query = query.order_by(NBPermit.created_at.desc())
        result = await db.execute(query)
        permits = result.scalars().all()

        items = []
        for p in permits:
            items.append({
                "id": p.id,
                "permit_code": p.permit_code,
                "student_name": getattr(p, 'student_name', ''),
                "subject_name": p.subject_name,
                "teacher_name": getattr(p, 'teacher_name', ''),
                "permit_type": getattr(p, 'permit_type', ''),
                "status": p.status,
                "created_at": str(p.created_at) if p.created_at else None,
                "deadline": str(p.deadline) if getattr(p, 'deadline', None) else None,
            })

        return {"items": items, "total": len(items)}

    except ImportError:
        return {"items": [], "total": 0}
