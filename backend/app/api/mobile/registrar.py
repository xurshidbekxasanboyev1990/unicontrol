"""
UniControl - Mobile Registrar Panel
=====================================
Registrar office mobile endpoints:
dashboard, students, student detail, attendance,
NB permits CRUD, verify QR, groups, teachers.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.nb_permit import NBPermit, PermitStatus
from app.core.dependencies import get_current_active_user
from app.config import today_tashkent

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_mobile_registrar(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require registrar role for mobile."""
    if current_user.role not in [
        UserRole.REGISTRAR_OFFICE,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ]:
        raise HTTPException(status_code=403, detail="Registratura ruxsati kerak")
    return current_user


# ============================================
# Schemas
# ============================================

class MobileNBPermitCreate(BaseModel):
    student_id: int
    subject_name: str
    semester: int = 1
    academic_year: str = "2025-2026"
    nb_type: str = "nb"
    reason: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    expiry_date: Optional[date] = None
    registrar_notes: Optional[str] = None


class MobileNBPermitUpdate(BaseModel):
    status: Optional[str] = None
    result_grade: Optional[str] = None
    teacher_notes: Optional[str] = None
    registrar_notes: Optional[str] = None


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def mobile_registrar_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Registrar mobile dashboard stats."""
    today = today_tashkent()

    total_students = await db.scalar(
        select(func.count(Student.id)).where(Student.is_active == True)
    ) or 0

    total_groups = await db.scalar(
        select(func.count(Group.id)).where(Group.is_active == True)
    ) or 0

    today_present = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.date == today, Attendance.status == AttendanceStatus.PRESENT)
        )
    ) or 0

    today_absent = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.date == today, Attendance.status == AttendanceStatus.ABSENT)
        )
    ) or 0

    total_permits = await db.scalar(select(func.count(NBPermit.id))) or 0

    active_permits = await db.scalar(
        select(func.count(NBPermit.id)).where(
            NBPermit.status.in_(
                [PermitStatus.ISSUED, PermitStatus.PENDING, PermitStatus.IN_PROGRESS]
            )
        )
    ) or 0

    approved_permits = await db.scalar(
        select(func.count(NBPermit.id)).where(NBPermit.status == PermitStatus.APPROVED)
    ) or 0

    return {
        "role": "registrar",
        "total_students": total_students,
        "total_groups": total_groups,
        "today_present": today_present,
        "today_absent": today_absent,
        "total_permits": total_permits,
        "active_permits": active_permits,
        "approved_permits": approved_permits,
    }


# ============================================
# STUDENTS
# ============================================

@router.get("/students")
async def mobile_registrar_students(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get students with filters."""
    query = select(Student).where(Student.is_active == True)

    if search:
        sf = f"%{search}%"
        query = query.where(
            or_(
                Student.name.ilike(sf),
                Student.student_id.ilike(sf),
                Student.phone.ilike(sf),
                Student.passport.ilike(sf),
            )
        )
    if group_id:
        query = query.where(Student.group_id == group_id)
    if faculty:
        query = query.join(Group, Student.group_id == Group.id).where(
            Group.faculty == faculty
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

    query = query.order_by(Student.name).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()

    items = []
    for s in students:
        items.append(
            {
                "id": s.id,
                "student_id": s.student_id,
                "name": s.name,
                "phone": s.phone,
                "group_id": s.group_id,
                "group_name": s.group.name if s.group else None,
                "faculty": s.group.faculty if s.group else None,
                "contract_amount": float(s.contract_amount),
                "contract_paid": float(s.contract_paid),
                "is_active": s.is_active,
            }
        )

    return {"items": items, "total": total, "page": page}


@router.get("/students/{student_id}")
async def mobile_registrar_student_detail(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get student full details with NB permits and attendance stats."""
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    # Attendance stats
    total_days = await db.scalar(
        select(func.count(Attendance.id)).where(Attendance.student_id == student_id)
    ) or 0
    present_days = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(
                Attendance.student_id == student_id,
                Attendance.status == AttendanceStatus.PRESENT,
            )
        )
    ) or 0
    absent_days = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(
                Attendance.student_id == student_id,
                Attendance.status == AttendanceStatus.ABSENT,
            )
        )
    ) or 0

    # NB permits
    permits_result = await db.execute(
        select(NBPermit)
        .where(NBPermit.student_id == student_id)
        .order_by(NBPermit.created_at.desc())
    )
    permits = permits_result.scalars().all()

    return {
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
            "phone": student.phone,
            "email": student.email,
            "passport": student.passport,
            "jshshir": student.jshshir,
            "birth_date": str(student.birth_date) if student.birth_date else None,
            "gender": student.gender,
            "group_id": student.group_id,
            "group_name": student.group.name if student.group else None,
            "faculty": student.group.faculty if student.group else None,
            "contract_amount": float(student.contract_amount),
            "contract_paid": float(student.contract_paid),
            "is_active": student.is_active,
        },
        "attendance": {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "attendance_rate": round(present_days / total_days * 100, 1) if total_days > 0 else 0,
        },
        "permits": [
            {
                "id": p.id,
                "permit_code": p.permit_code,
                "subject_name": p.subject_name,
                "nb_type": p.nb_type,
                "status": p.status if isinstance(p.status, str) else p.status.value,
                "teacher_name": p.teacher_name,
                "issue_date": str(p.issue_date),
                "expiry_date": str(p.expiry_date) if p.expiry_date else None,
                "result_grade": p.result_grade,
            }
            for p in permits
        ],
    }


# ============================================
# ATTENDANCE (read-only)
# ============================================

@router.get("/attendance")
async def mobile_registrar_attendance(
    date_val: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get attendance records."""
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
        query = select(Attendance).where(
            Attendance.date >= d_from, Attendance.date <= d_to
        )
    else:
        target = today
        if date_val:
            try:
                target = date.fromisoformat(date_val)
            except ValueError:
                pass
        query = select(Attendance).where(Attendance.date == target)

    if group_id:
        query = query.join(Student, Attendance.student_id == Student.id).where(
            Student.group_id == group_id
        )
    if status_filter:
        try:
            query = query.where(Attendance.status == AttendanceStatus(status_filter))
        except ValueError:
            pass

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

    query = query.order_by(Attendance.id).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    items = []
    for a in records:
        items.append(
            {
                "id": a.id,
                "student_id": a.student_id,
                "student_name": a.student_name,
                "group_name": getattr(a, "group_name", ""),
                "date": str(a.date),
                "status": a.status.value if hasattr(a.status, "value") else a.status,
                "subject": a.subject,
                "lesson_number": a.lesson_number,
                "late_minutes": a.late_minutes,
            }
        )

    stats = {
        "total": total,
        "present": sum(1 for i in items if i["status"] == "present"),
        "absent": sum(1 for i in items if i["status"] == "absent"),
        "late": sum(1 for i in items if i["status"] == "late"),
        "excused": sum(1 for i in items if i["status"] == "excused"),
    }

    return {"items": items, "total": total, "stats": stats, "page": page}


# ============================================
# NB PERMITS — CRUD
# ============================================

@router.get("/permits")
async def mobile_registrar_permits(
    status_filter: Optional[str] = None,
    student_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get all NB permits."""
    query = select(NBPermit)

    if status_filter:
        query = query.where(NBPermit.status == status_filter)
    if student_id:
        query = query.where(NBPermit.student_id == student_id)
    if search:
        sf = f"%{search}%"
        query = query.where(
            or_(
                NBPermit.permit_code.ilike(sf),
                NBPermit.subject_name.ilike(sf),
            )
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

    query = (
        query.order_by(NBPermit.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await db.execute(query)
    permits = result.scalars().all()

    items = []
    for p in permits:
        items.append(
            {
                "id": p.id,
                "permit_code": p.permit_code,
                "student_id": p.student_id,
                "student_name": p.student.name if p.student else None,
                "group_name": p.group.name if p.group else None,
                "subject_name": p.subject_name,
                "semester": p.semester,
                "academic_year": p.academic_year,
                "nb_type": p.nb_type,
                "reason": p.reason,
                "teacher_name": p.teacher_name,
                "issued_by_name": p.issued_by_name,
                "issue_date": str(p.issue_date),
                "expiry_date": str(p.expiry_date) if p.expiry_date else None,
                "status": p.status if isinstance(p.status, str) else p.status.value,
                "result_grade": p.result_grade,
                "print_count": p.print_count,
            }
        )

    return {"items": items, "total": total, "page": page}


@router.post("/permits")
async def mobile_registrar_create_permit(
    data: MobileNBPermitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Create a new NB permit from mobile."""
    student = await db.get(Student, data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    permit_code = NBPermit.generate_permit_code()
    today = today_tashkent()
    verification_hash = NBPermit.generate_verification_hash(
        permit_code, data.student_id, data.subject_name, str(today)
    )

    permit = NBPermit(
        permit_code=permit_code,
        verification_hash=verification_hash,
        student_id=data.student_id,
        group_id=student.group_id,
        subject_name=data.subject_name,
        semester=data.semester,
        academic_year=data.academic_year,
        nb_type=data.nb_type,
        reason=data.reason,
        teacher_id=data.teacher_id,
        teacher_name=data.teacher_name,
        issued_by=current_user.id,
        issued_by_name=current_user.name,
        issue_date=today,
        expiry_date=data.expiry_date,
        status=PermitStatus.ISSUED,
        registrar_notes=data.registrar_notes,
    )

    db.add(permit)
    await db.commit()
    await db.refresh(permit)

    return {
        "id": permit.id,
        "permit_code": permit.permit_code,
        "status": permit.status,
        "message": "Ruxsatnoma yaratildi",
    }


@router.put("/permits/{permit_id}")
async def mobile_registrar_update_permit(
    permit_id: int,
    data: MobileNBPermitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Update permit status/notes."""
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")

    if data.status:
        permit.status = data.status
        if data.status in [PermitStatus.APPROVED, "approved"]:
            permit.completed_date = today_tashkent()
    if data.result_grade is not None:
        permit.result_grade = data.result_grade
    if data.teacher_notes is not None:
        permit.teacher_notes = data.teacher_notes
    if data.registrar_notes is not None:
        permit.registrar_notes = data.registrar_notes

    await db.commit()
    return {"message": "Ruxsatnoma yangilandi"}


@router.delete("/permits/{permit_id}")
async def mobile_registrar_delete_permit(
    permit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Delete/cancel permit."""
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")

    if permit.status not in [PermitStatus.ISSUED, PermitStatus.CANCELLED]:
        permit.status = PermitStatus.CANCELLED
        await db.commit()
        return {"message": "Ruxsatnoma bekor qilindi"}

    await db.delete(permit)
    await db.commit()
    return {"message": "Ruxsatnoma o'chirildi"}


# ============================================
# VERIFY PERMIT (QR code)
# ============================================

@router.get("/verify/{permit_code}")
async def mobile_registrar_verify_permit(
    permit_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify permit by code — QR scan from mobile."""
    result = await db.execute(
        select(NBPermit).where(NBPermit.permit_code == permit_code)
    )
    permit = result.scalar_one_or_none()

    if not permit:
        return {"valid": False, "message": "Ruxsatnoma topilmadi"}

    is_authentic = permit.verify()
    student = await db.get(Student, permit.student_id)

    return {
        "valid": is_authentic,
        "permit_code": permit.permit_code,
        "student_name": student.name if student else None,
        "group_name": student.group.name if student and student.group else None,
        "subject_name": permit.subject_name,
        "nb_type": permit.nb_type,
        "status": permit.status if isinstance(permit.status, str) else permit.status.value,
        "issue_date": str(permit.issue_date),
        "expiry_date": str(permit.expiry_date) if permit.expiry_date else None,
        "result_grade": permit.result_grade,
        "is_approved": permit.status in [PermitStatus.APPROVED, "approved"],
    }


# ============================================
# GROUPS (dropdown)
# ============================================

@router.get("/groups")
async def mobile_registrar_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get all active groups."""
    result = await db.execute(
        select(Group).where(Group.is_active == True).order_by(Group.name)
    )
    groups = result.scalars().all()

    return {
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "faculty": g.faculty,
                "course_year": g.course_year,
            }
            for g in groups
        ]
    }


# ============================================
# TEACHERS (dropdown for permit assignment)
# ============================================

@router.get("/teachers")
async def mobile_registrar_teachers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mobile_registrar),
):
    """Get teachers list for permit assignment."""
    result = await db.execute(
        select(User)
        .where(and_(User.role == UserRole.TEACHER, User.is_active == True))
        .order_by(User.name)
    )
    teachers = result.scalars().all()

    return {
        "teachers": [{"id": t.id, "name": t.name} for t in teachers]
    }
