"""
UniControl - Mobile Dean Panel
================================
Dean mobile endpoints matching web v1/dean exactly:
- Dashboard statistics
- Students kontingent (read-only)
- Faculties + faculties-tree
- Groups
- Attendance (view + export + import)
- Schedule (read-only)
- Workload + departments
- Contracts (filters + list with stats)
- NB Permits (read-only)

Author: UniControl Team
Version: 2.0.0
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

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_mobile_dean(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in [UserRole.DEAN, UserRole.ADMIN, UserRole.SUPERADMIN]:
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
    """Dean mobile dashboard — matches web v1/dean/dashboard."""
    today = today_tashkent()

    total_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0

    total_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.is_active == True)
    )).scalar() or 0

    # Attendance stats in one query
    att_row = (await db.execute(
        select(
            func.count(Attendance.id).label("total"),
            func.count(Attendance.id).filter(
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
            ).label("present"),
            func.count(Attendance.id).filter(
                Attendance.status == AttendanceStatus.ABSENT
            ).label("absent"),
        ).where(Attendance.date == today)
    )).one()
    total_today = att_row.total or 0
    present_count = att_row.present or 0
    absent_count = att_row.absent or 0
    attendance_rate = round(present_count / total_today * 100, 1) if total_today > 0 else 0

    # Today lessons
    day_map = {0: WeekDay.MONDAY, 1: WeekDay.TUESDAY, 2: WeekDay.WEDNESDAY,
               3: WeekDay.THURSDAY, 4: WeekDay.FRIDAY, 5: WeekDay.SATURDAY, 6: WeekDay.SUNDAY}
    today_weekday = day_map[today.weekday()]
    today_lessons = (await db.execute(
        select(func.count(Schedule.id)).where(
            and_(Schedule.is_active == True, Schedule.is_cancelled == False, Schedule.day_of_week == today_weekday)
        )
    )).scalar() or 0

    # NB permits stats
    nb_stats = {"total": 0, "active": 0, "approved": 0}
    try:
        from app.models.nb_permit import NBPermit, PermitStatus
        nb_row = (await db.execute(
            select(
                func.count(NBPermit.id).label("total"),
                func.count(NBPermit.id).filter(
                    NBPermit.status.in_([PermitStatus.ISSUED, PermitStatus.PENDING, PermitStatus.IN_PROGRESS])
                ).label("active"),
                func.count(NBPermit.id).filter(NBPermit.status == PermitStatus.APPROVED).label("approved"),
            )
        )).one()
        nb_stats = {"total": nb_row.total or 0, "active": nb_row.active or 0, "approved": nb_row.approved or 0}
    except Exception:
        pass

    # Contract stats
    contract_stats = {"total": 0, "paid": 0, "debt": 0}
    try:
        from app.models.contract import Contract
        row = (await db.execute(
            select(func.count(Contract.id), func.coalesce(func.sum(Contract.total_paid), 0),
                   func.coalesce(func.sum(Contract.contract_amount), 0))
        )).one()
        contract_stats["total"] = row[0] or 0
        contract_stats["paid"] = float(row[1] or 0)
        contract_stats["debt"] = float((row[2] or 0) - (row[1] or 0))
    except Exception:
        pass

    return {
        "total_students": total_students, "total_groups": total_groups,
        "today_present": present_count, "today_absent": absent_count,
        "attendance_rate": attendance_rate, "today_lessons": today_lessons,
        "nb_stats": nb_stats, "contract_stats": contract_stats,
    }


# ============================================
# STUDENTS (Read-only)
# ============================================

@router.get("/students")
async def mobile_dean_students(
    search: Optional[str] = None, group_id: Optional[int] = None,
    faculty: Optional[str] = None, course_year: Optional[int] = None,
    page: int = 1, per_page: int = 50,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Students list — matches web v1/dean/students."""
    query = select(Student).where(Student.is_active == True)

    if search:
        query = query.where(or_(
            Student.name.ilike(f"%{search}%"), Student.student_id.ilike(f"%{search}%"),
            Student.phone.ilike(f"%{search}%"),
        ))
    if group_id:
        query = query.where(Student.group_id == group_id)
    if faculty:
        fac_ids = [r[0] for r in (await db.execute(
            select(Group.id).where(and_(Group.is_active == True, Group.faculty == faculty))
        )).all()]
        query = query.where(Student.group_id.in_(fac_ids)) if fac_ids else query.where(Student.id == -1)
    if course_year:
        crs_ids = [r[0] for r in (await db.execute(
            select(Group.id).where(and_(Group.is_active == True, Group.course_year == course_year))
        )).all()]
        query = query.where(Student.group_id.in_(crs_ids)) if crs_ids else query.where(Student.id == -1)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    offset = (page - 1) * per_page
    query = query.options(joinedload(Student.group)).order_by(Student.name).offset(offset).limit(per_page)
    students = (await db.execute(query)).scalars().unique().all()

    items = [{
        "id": s.id, "name": s.name, "student_id": s.student_id, "hemis_id": s.hemis_id,
        "group_id": s.group_id, "group_name": s.group.name if s.group else "",
        "phone": s.phone, "email": s.email,
        "passport": getattr(s, "passport", None), "address": getattr(s, "address", None),
        "is_active": s.is_active,
        "contract_amount": float(getattr(s, "contract_amount", 0) or 0),
        "contract_paid": float(getattr(s, "contract_paid", 0) or 0),
    } for s in students]

    return {"items": items, "total": total, "page": page, "per_page": per_page}


# ============================================
# FACULTIES & GROUPS
# ============================================

@router.get("/faculties")
async def mobile_dean_faculties(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Faculties list — matches web v1/dean/faculties."""
    result = await db.execute(
        select(distinct(Group.faculty))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != ""))
        .order_by(Group.faculty)
    )
    return {"faculties": [r[0] for r in result.all() if r[0]]}


@router.get("/faculties-tree")
async def mobile_dean_faculties_tree(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Faculty tree with groups — matches web v1/dean/faculties-tree."""
    result = await db.execute(
        select(Group.id, Group.name, Group.faculty, Group.course_year,
               func.count(Student.id).label("students_count"))
        .outerjoin(Student, and_(Student.group_id == Group.id, Student.is_active == True))
        .where(Group.is_active == True)
        .group_by(Group.id, Group.name, Group.faculty, Group.course_year)
        .order_by(Group.faculty, Group.name)
    )
    rows = result.all()
    faculty_map = {}
    for row in rows:
        fname = row.faculty or "Boshqa"
        if fname not in faculty_map:
            faculty_map[fname] = []
        faculty_map[fname].append({
            "id": row.id, "name": row.name, "course_year": row.course_year,
            "students_count": row.students_count or 0,
        })

    faculties = []
    for fname in sorted(faculty_map.keys()):
        groups = faculty_map[fname]
        faculties.append({
            "name": fname,
            "directions": [{"name": fname, "groups": sorted(groups, key=lambda g: g["name"]),
                            "groups_count": len(groups),
                            "students_count": sum(g["students_count"] for g in groups)}],
            "directions_count": 1, "groups_count": len(groups),
            "students_count": sum(g["students_count"] for g in groups),
        })
    return {
        "faculties": faculties, "total_faculties": len(faculties),
        "total_directions": len(faculties),
        "total_groups": sum(f["groups_count"] for f in faculties),
    }


@router.get("/groups")
async def mobile_dean_groups(
    faculty: Optional[str] = None, course_year: Optional[int] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Groups list — matches web v1/dean/groups."""
    query = (
        select(Group, func.count(Student.id).label("students_count"))
        .outerjoin(Student, and_(Student.group_id == Group.id, Student.is_active == True))
        .where(Group.is_active == True)
    )
    if faculty:
        query = query.where(Group.faculty == faculty)
    if course_year:
        query = query.where(Group.course_year == course_year)
    query = query.group_by(Group.id).order_by(Group.name)
    rows = (await db.execute(query)).all()

    return {"items": [{"id": g.id, "name": g.name, "faculty": g.faculty,
                        "course_year": g.course_year, "students_count": cnt or 0}
                       for g, cnt in rows], "total": len(rows)}


# ============================================
# ATTENDANCE (Read-only + export + import)
# ============================================

@router.get("/attendance")
async def mobile_dean_attendance(
    date_val: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None,
    group_id: Optional[int] = None, status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Attendance records — matches web v1/dean/attendance."""
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
        query = select(Attendance).join(Student, Student.id == Attendance.student_id).where(
            and_(Attendance.date >= d_from, Attendance.date <= d_to))
    else:
        target = today
        if date_val:
            try:
                target = date.fromisoformat(date_val)
            except ValueError:
                pass
        query = select(Attendance).join(Student, Student.id == Attendance.student_id).where(Attendance.date == target)

    if group_id:
        query = query.where(Student.group_id == group_id)
    if status_filter:
        try:
            query = query.where(Attendance.status == AttendanceStatus(status_filter))
        except ValueError:
            pass

    records = (await db.execute(query.order_by(Student.name))).scalars().all()
    stats = {"total": 0, "present": 0, "absent": 0, "late": 0, "excused": 0}
    items = []
    for a in records:
        stats["total"] += 1
        if a.status == AttendanceStatus.PRESENT: stats["present"] += 1
        elif a.status == AttendanceStatus.ABSENT: stats["absent"] += 1
        elif a.status == AttendanceStatus.LATE: stats["late"] += 1
        elif a.status == AttendanceStatus.EXCUSED: stats["excused"] += 1
        items.append({
            "id": a.id, "student_id": a.student_id, "student_name": a.student_name,
            "group_name": getattr(a, "group_name", ""), "subject": a.subject,
            "lesson_number": a.lesson_number, "status": a.status.value,
            "check_in_time": a.check_in_time.strftime("%H:%M") if a.check_in_time else None,
            "note": getattr(a, "note", ""),
        })
    return {"items": items, "stats": stats}


@router.get("/attendance/export")
async def mobile_dean_attendance_export(
    date_val: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None,
    group_id: Optional[int] = None, status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Export attendance to Excel — matches web v1/dean/attendance/export."""
    from fastapi.responses import StreamingResponse
    from app.services.excel_service import ExcelService

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
    else:
        d_from = today
        if date_val:
            try:
                d_from = date.fromisoformat(date_val)
            except ValueError:
                pass
        d_to = d_from

    service = ExcelService(db)
    file_data = await service.export_attendance_printable(
        group_id=group_id, date_from=d_from, date_to=d_to, status_filter=status_filter,
    )
    fname_parts = ["davomat", d_from.strftime("%d_%m_%Y")]
    if d_from != d_to:
        fname_parts.append(d_to.strftime("%d_%m_%Y"))
    if group_id:
        fname_parts.insert(1, f"guruh_{group_id}")
    filename = "_".join(fname_parts) + ".xlsx"

    return StreamingResponse(
        file_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/attendance/import")
async def mobile_dean_attendance_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Import attendance from Excel — matches web v1/dean/attendance/import."""
    import io
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl kutubxonasi o'rnatilmagan")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Faqat Excel (.xlsx) fayl yuklash mumkin")

    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="Fayl bo'sh yoki sarlavha qatori topilmadi")

    header = [str(c).strip().lower() if c else "" for c in rows[0]]
    col_map = {}
    for i, h in enumerate(header):
        if h in ("student_id", "talaba_id", "hemis_id", "id"): col_map["student_id"] = i
        elif h in ("date", "sana", "kun"): col_map["date"] = i
        elif h in ("status", "holat", "davomat"): col_map["status"] = i
        elif h in ("subject", "fan", "dars"): col_map["subject"] = i
        elif h in ("lesson", "lesson_number", "dars_raqami", "para"): col_map["lesson_number"] = i

    if "student_id" not in col_map or "status" not in col_map:
        raise HTTPException(status_code=400,
                            detail="Excel faylda 'student_id' va 'status' ustunlari topilmadi. Ustunlar: " + ", ".join(header))

    status_map = {
        "kelgan": "present", "present": "present", "bor": "present", "+": "present", "1": "present",
        "kelmagan": "absent", "absent": "absent", "yoq": "absent", "-": "absent", "0": "absent",
        "kechikkan": "late", "late": "late", "kech": "late",
        "sababli": "excused", "excused": "excused", "uzr": "excused",
    }

    created = updated = 0
    errors = []
    for row_idx, row in enumerate(rows[1:], start=2):
        try:
            sid_val = str(row[col_map["student_id"]]).strip() if row[col_map["student_id"]] else None
            if not sid_val:
                continue
            student = (await db.execute(select(Student).where(Student.student_id == sid_val))).scalar_one_or_none()
            if not student:
                try:
                    student = (await db.execute(select(Student).where(Student.id == int(sid_val)))).scalar_one_or_none()
                except (ValueError, TypeError):
                    pass
            if not student:
                errors.append(f"Qator {row_idx}: Talaba topilmadi ({sid_val})")
                continue

            att_date = today_tashkent()
            if "date" in col_map and row[col_map["date"]]:
                raw = row[col_map["date"]]
                if isinstance(raw, datetime): att_date = raw.date()
                elif isinstance(raw, date): att_date = raw
                else:
                    try:
                        att_date = date.fromisoformat(str(raw).strip())
                    except ValueError:
                        pass

            raw_st = str(row[col_map["status"]]).strip().lower() if row[col_map["status"]] else "absent"
            try:
                att_status = AttendanceStatus(status_map.get(raw_st, "absent"))
            except ValueError:
                att_status = AttendanceStatus.ABSENT

            subject = None
            if "subject" in col_map and row[col_map["subject"]]:
                subject = str(row[col_map["subject"]]).strip()
            lesson_number = None
            if "lesson_number" in col_map and row[col_map["lesson_number"]]:
                try:
                    lesson_number = int(row[col_map["lesson_number"]])
                except (ValueError, TypeError):
                    pass

            existing = (await db.execute(
                select(Attendance).where(and_(
                    Attendance.student_id == student.id, Attendance.date == att_date,
                    or_(Attendance.lesson_number == lesson_number,
                        and_(Attendance.lesson_number.is_(None), lesson_number is None))
                ))
            )).scalar_one_or_none()

            if existing:
                existing.status = att_status
                existing.subject = subject or existing.subject
                existing.recorded_by = current_user.id
                updated += 1
            else:
                db.add(Attendance(student_id=student.id, date=att_date, status=att_status,
                                  subject=subject, lesson_number=lesson_number, recorded_by=current_user.id))
                created += 1
        except Exception as e:
            errors.append(f"Qator {row_idx}: {str(e)}")

    await db.commit()
    return {"success": True, "message": f"Import tugallandi: {created} yangi, {updated} yangilandi",
            "created": created, "updated": updated, "errors": errors[:20], "total_errors": len(errors)}


# ============================================
# SCHEDULE (Read-only)
# ============================================

@router.get("/schedule")
async def mobile_dean_schedule(
    group_id: Optional[int] = None, faculty: Optional[str] = None,
    course_year: Optional[int] = None, teacher: Optional[str] = None,
    page: int = 1, per_page: int = 100,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Schedule — matches web v1/dean/schedule."""
    query = select(Schedule).options(joinedload(Schedule.group)).where(Schedule.is_active == True)
    if group_id:
        query = query.where(Schedule.group_id == group_id)
    if faculty:
        fac_subq = select(Group.id).where(and_(Group.is_active == True, Group.faculty == faculty)).scalar_subquery()
        query = query.where(Schedule.group_id.in_(fac_subq))
    if course_year:
        crs_subq = select(Group.id).where(and_(Group.is_active == True, Group.course_year == course_year)).scalar_subquery()
        query = query.where(Schedule.group_id.in_(crs_subq))
    if teacher:
        query = query.where(Schedule.teacher_name.ilike(f"%{teacher}%"))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    offset = (page - 1) * per_page
    query = query.order_by(Schedule.day_of_week, Schedule.start_time).offset(offset).limit(per_page)
    schedules = (await db.execute(query)).unique().scalars().all()

    items = [{
        "id": s.id, "subject": s.subject, "subject_code": s.subject_code,
        "group_id": s.group_id, "group_name": s.group.name if s.group else None,
        "teacher_name": s.teacher_name,
        "day_of_week": s.day_of_week.value if s.day_of_week else None,
        "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
        "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
        "time_range": s.time_range, "room": s.room, "building": s.building,
        "lesson_number": s.lesson_number,
        "week_type": s.week_type.value if s.week_type else "all",
        "schedule_type": s.schedule_type.value if s.schedule_type else None,
        "is_cancelled": s.is_cancelled,
    } for s in schedules]
    return {"items": items, "total": total, "page": page, "per_page": per_page}


# ============================================
# WORKLOAD (Read-only)
# ============================================

@router.get("/workload")
async def mobile_dean_workload(
    search: Optional[str] = None, department: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Workload — matches web v1/dean/workload."""
    query = select(TeacherWorkload).where(TeacherWorkload.is_active == True)
    if search: query = query.where(TeacherWorkload.teacher_name.ilike(f"%{search}%"))
    if department: query = query.where(TeacherWorkload.department.ilike(f"%{department}%"))
    query = query.order_by(
        TeacherWorkload.teacher_name,
        case((TeacherWorkload.day_of_week == "monday", 1), (TeacherWorkload.day_of_week == "tuesday", 2),
             (TeacherWorkload.day_of_week == "wednesday", 3), (TeacherWorkload.day_of_week == "thursday", 4),
             (TeacherWorkload.day_of_week == "friday", 5), (TeacherWorkload.day_of_week == "saturday", 6), else_=7),
        TeacherWorkload.lesson_number,
    )
    workloads = (await db.execute(query)).scalars().all()
    return {"items": [{
        "id": w.id, "teacher_name": w.teacher_name, "department": w.department,
        "teacher_type": w.teacher_type, "day_of_week": w.day_of_week, "day_name_uz": w.day_name_uz,
        "lesson_number": w.lesson_number, "start_time": w.start_time, "end_time": w.end_time,
        "groups": w.groups, "is_busy": w.is_busy,
    } for w in workloads], "total": len(workloads)}


@router.get("/workload/departments")
async def mobile_dean_workload_departments(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Departments list — matches web v1/dean/workload/departments."""
    result = await db.execute(
        select(distinct(TeacherWorkload.department))
        .where(and_(TeacherWorkload.is_active == True, TeacherWorkload.department.isnot(None), TeacherWorkload.department != ""))
        .order_by(TeacherWorkload.department)
    )
    return {"departments": [r[0] for r in result.all() if r[0]]}


# ============================================
# CONTRACTS (Read-only)
# ============================================

@router.get("/contracts/filters")
async def mobile_dean_contracts_filters(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Contract filter options — matches web v1/dean/contracts/filters."""
    try:
        from app.models.contract import Contract

        fac = [r[0] for r in (await db.execute(
            select(distinct(Group.faculty)).where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != "")).order_by(Group.faculty)
        )).all() if r[0]]
        dirs = [r[0] for r in (await db.execute(
            select(distinct(Contract.direction)).where(and_(Contract.direction.isnot(None), Contract.direction != "")).order_by(Contract.direction)
        )).all() if r[0]]
        ef = [r[0] for r in (await db.execute(
            select(distinct(Contract.education_form)).where(and_(Contract.education_form.isnot(None), Contract.education_form != "")).order_by(Contract.education_form)
        )).all() if r[0]]
        courses = [r[0] for r in (await db.execute(
            select(distinct(Contract.course)).where(Contract.course.isnot(None)).order_by(Contract.course)
        )).all() if r[0]]
        ay = [r[0] for r in (await db.execute(
            select(distinct(Contract.academic_year)).where(and_(Contract.academic_year.isnot(None), Contract.academic_year != "")).order_by(Contract.academic_year)
        )).all() if r[0]]

        return {"faculties": fac, "directions": dirs, "education_forms": ef, "courses": courses, "academic_years": ay}
    except Exception:
        return {"faculties": [], "directions": [], "education_forms": [], "courses": [], "academic_years": []}


@router.get("/contracts")
async def mobile_dean_contracts(
    search: Optional[str] = None, group_id: Optional[int] = None,
    faculty: Optional[str] = None, direction: Optional[str] = None,
    course: Optional[str] = None, education_form: Optional[str] = None,
    academic_year: Optional[str] = None, has_debt: Optional[bool] = None,
    page: int = 1, per_page: int = 50,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """Contracts list with stats — matches web v1/dean/contracts."""
    try:
        from app.models.contract import Contract

        query = (
            select(Contract).join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
            .options(joinedload(Contract.student).joinedload(Student.group))
        )
        if search:
            query = query.where(or_(Student.name.ilike(f"%{search}%"), Student.student_id.ilike(f"%{search}%")))
        if group_id: query = query.where(Student.group_id == group_id)
        if faculty: query = query.where(Group.faculty == faculty)
        if direction: query = query.where(Contract.direction == direction)
        if course: query = query.where(Contract.course == course)
        if education_form: query = query.where(Contract.education_form == education_form)
        if academic_year: query = query.where(Contract.academic_year == academic_year)
        if has_debt is True: query = query.where(Contract.total_paid < Contract.contract_amount)
        elif has_debt is False: query = query.where(Contract.total_paid >= Contract.contract_amount)

        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

        # Stats
        stats_q = (
            select(func.count(Contract.id), func.coalesce(func.sum(Contract.contract_amount), 0),
                   func.coalesce(func.sum(Contract.total_paid), 0))
            .join(Student, Student.id == Contract.student_id).outerjoin(Group, Group.id == Student.group_id)
        )
        if search: stats_q = stats_q.where(or_(Student.name.ilike(f"%{search}%"), Student.student_id.ilike(f"%{search}%")))
        if group_id: stats_q = stats_q.where(Student.group_id == group_id)
        if faculty: stats_q = stats_q.where(Group.faculty == faculty)
        if direction: stats_q = stats_q.where(Contract.direction == direction)
        if course: stats_q = stats_q.where(Contract.course == course)
        if education_form: stats_q = stats_q.where(Contract.education_form == education_form)
        if academic_year: stats_q = stats_q.where(Contract.academic_year == academic_year)
        if has_debt is True: stats_q = stats_q.where(Contract.total_paid < Contract.contract_amount)
        elif has_debt is False: stats_q = stats_q.where(Contract.total_paid >= Contract.contract_amount)

        sr = (await db.execute(stats_q)).one()
        total_amount = float(sr[1] or 0)
        total_paid_val = float(sr[2] or 0)
        stats = {
            "total": sr[0] or 0, "paid": 0, "unpaid": 0,
            "total_contract_amount": total_amount, "total_paid": total_paid_val,
            "total_debt": total_amount - total_paid_val,
            "payment_percentage": round(total_paid_val / max(total_amount, 1) * 100, 1),
        }

        paid_count_q = (
            select(func.count(Contract.id)).join(Student, Student.id == Contract.student_id)
            .outerjoin(Group, Group.id == Student.group_id)
            .where(Contract.total_paid >= Contract.contract_amount)
        )
        if group_id: paid_count_q = paid_count_q.where(Student.group_id == group_id)
        if faculty: paid_count_q = paid_count_q.where(Group.faculty == faculty)
        if direction: paid_count_q = paid_count_q.where(Contract.direction == direction)
        if course: paid_count_q = paid_count_q.where(Contract.course == course)
        if education_form: paid_count_q = paid_count_q.where(Contract.education_form == education_form)
        if academic_year: paid_count_q = paid_count_q.where(Contract.academic_year == academic_year)
        stats["paid"] = (await db.execute(paid_count_q)).scalar() or 0
        stats["unpaid"] = (sr[0] or 0) - stats["paid"]

        offset = (page - 1) * per_page
        query = query.order_by(Student.name).offset(offset).limit(per_page)
        contracts = (await db.execute(query)).unique().scalars().all()

        items = []
        for c in contracts:
            debt = float((c.contract_amount or 0) - (c.total_paid or 0))
            items.append({
                "id": c.id, "student_name": c.student_name,
                "student_id_number": getattr(c, "student_jshshir", "") or getattr(c, "student_id_number", ""),
                "group_name": getattr(c, "group_name", ""), "direction": c.direction or "",
                "course": c.course or "", "education_form": c.education_form or "",
                "contract_amount": float(c.contract_amount or 0), "paid_amount": float(c.total_paid or 0),
                "debt": debt, "is_paid": debt <= 0,
                "academic_year": c.academic_year, "grant_percentage": float(c.grant_percentage or 0),
            })
        return {"items": items, "total": total, "stats": stats}
    except ImportError:
        return {"items": [], "total": 0, "stats": {}}


# ============================================
# NB PERMITS (Read-only)
# ============================================

@router.get("/nb-permits")
async def mobile_dean_nb_permits(
    search: Optional[str] = None, status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_mobile_dean),
):
    """NB permits — matches web v1/dean/nb-permits."""
    try:
        from app.models.nb_permit import NBPermit
        query = select(NBPermit).options(joinedload(NBPermit.student))
        if search:
            query = query.join(Student, Student.id == NBPermit.student_id, isouter=True).where(or_(
                NBPermit.permit_code.ilike(f"%{search}%"), NBPermit.subject_name.ilike(f"%{search}%"),
                Student.name.ilike(f"%{search}%"),
            ))
        if status_filter:
            query = query.where(NBPermit.status == status_filter)
        query = query.order_by(NBPermit.created_at.desc())
        permits = (await db.execute(query)).unique().scalars().all()
        return {"items": [{
            "id": p.id, "permit_code": p.permit_code,
            "student_name": p.student.name if p.student else "",
            "subject_name": p.subject_name, "teacher_name": getattr(p, "teacher_name", ""),
            "permit_type": getattr(p, "nb_type", ""), "status": p.status,
            "created_at": str(p.created_at) if p.created_at else None,
            "deadline": str(p.expiry_date) if getattr(p, "expiry_date", None) else None,
        } for p in permits], "total": len(permits)}
    except ImportError:
        return {"items": [], "total": 0}
