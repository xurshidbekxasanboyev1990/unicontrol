"""
UniControl - Registrar Office API
====================================
API endpoints for registrar_office role.
- View attendance
- View student info
- Issue NB permits (atrabotka ruxsatnomasi)
- Manage permit statuses
- Print permits as checks

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from pydantic import BaseModel

from app.database import get_db
from app.config import TASHKENT_TZ
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.nb_permit import NBPermit, PermitStatus
from app.core.dependencies import get_current_active_user

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_registrar(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require registrar_office, admin, or superadmin role."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.REGISTRAR_OFFICE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registrator ofisi uchun ruxsat yo'q"
        )
    return current_user


async def require_registrar_or_teacher(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require registrar, teacher, admin, or superadmin."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.REGISTRAR_OFFICE, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q"
        )
    return current_user


# ============================================
# Pydantic Schemas
# ============================================

class NBPermitCreate(BaseModel):
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


class NBPermitUpdate(BaseModel):
    status: Optional[str] = None
    result_grade: Optional[str] = None
    teacher_notes: Optional[str] = None
    registrar_notes: Optional[str] = None


class NBPermitTeacherUpdate(BaseModel):
    status: str  # approved / rejected
    result_grade: Optional[str] = None
    teacher_notes: Optional[str] = None


# ============================================
# DASHBOARD & STATS
# ============================================

@router.get("/dashboard")
async def get_registrar_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Registrar office dashboard stats."""
    today = date.today()
    
    # Total students
    total_students = await db.scalar(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    
    # Total groups
    total_groups = await db.scalar(
        select(func.count(Group.id)).where(Group.is_active == True)
    )
    
    # Today's attendance
    today_present = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.date == today, Attendance.status == AttendanceStatus.PRESENT)
        )
    )
    today_absent = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.date == today, Attendance.status == AttendanceStatus.ABSENT)
        )
    )
    
    # NB Permits stats
    total_permits = await db.scalar(select(func.count(NBPermit.id)))
    active_permits = await db.scalar(
        select(func.count(NBPermit.id)).where(
            NBPermit.status.in_([PermitStatus.ISSUED, PermitStatus.PENDING, PermitStatus.IN_PROGRESS])
        )
    )
    approved_permits = await db.scalar(
        select(func.count(NBPermit.id)).where(NBPermit.status == PermitStatus.APPROVED)
    )
    
    return {
        "total_students": total_students or 0,
        "total_groups": total_groups or 0,
        "today_present": today_present or 0,
        "today_absent": today_absent or 0,
        "total_permits": total_permits or 0,
        "active_permits": active_permits or 0,
        "approved_permits": approved_permits or 0,
    }


# ============================================
# STUDENTS
# ============================================

@router.get("/students")
async def get_students(
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    faculty: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get all students with filters."""
    query = select(Student).where(Student.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Student.name.ilike(search_filter),
                Student.student_id.ilike(search_filter),
                Student.phone.ilike(search_filter),
                Student.passport.ilike(search_filter)
            )
        )
    
    if group_id:
        query = query.where(Student.group_id == group_id)
    
    if faculty:
        query = query.join(Group, Student.group_id == Group.id).where(Group.faculty == faculty)
    
    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_q) or 0
    
    # Paginate
    query = query.order_by(Student.name).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()
    
    items = []
    for s in students:
        items.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "phone": s.phone,
            "email": s.email,
            "passport": s.passport,
            "jshshir": s.jshshir,
            "birth_date": str(s.birth_date) if s.birth_date else None,
            "gender": s.gender,
            "group_id": s.group_id,
            "group_name": s.group.name if s.group else None,
            "faculty": s.group.faculty if s.group else None,
            "course_year": s.group.course_year if s.group else None,
            "contract_amount": float(s.contract_amount),
            "contract_paid": float(s.contract_paid),
            "enrollment_date": str(s.enrollment_date) if s.enrollment_date else None,
            "is_active": s.is_active,
        })
    
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/students/{student_id}")
async def get_student_detail(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get student full details with NB permits."""
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    
    # Get student's NB permits
    permits_q = select(NBPermit).where(NBPermit.student_id == student_id).order_by(NBPermit.created_at.desc())
    permits_result = await db.execute(permits_q)
    permits = permits_result.scalars().all()
    
    # Get attendance stats
    total_days = await db.scalar(
        select(func.count(Attendance.id)).where(Attendance.student_id == student_id)
    ) or 0
    present_days = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.student_id == student_id, Attendance.status == AttendanceStatus.PRESENT)
        )
    ) or 0
    absent_days = await db.scalar(
        select(func.count(Attendance.id)).where(
            and_(Attendance.student_id == student_id, Attendance.status == AttendanceStatus.ABSENT)
        )
    ) or 0
    
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
            "address": student.address,
            "group_id": student.group_id,
            "group_name": student.group.name if student.group else None,
            "faculty": student.group.faculty if student.group else None,
            "course_year": student.group.course_year if student.group else None,
            "contract_amount": float(student.contract_amount),
            "contract_paid": float(student.contract_paid),
            "enrollment_date": str(student.enrollment_date) if student.enrollment_date else None,
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
                "semester": p.semester,
                "academic_year": p.academic_year,
                "nb_type": p.nb_type,
                "status": p.status,
                "teacher_name": p.teacher_name,
                "issue_date": str(p.issue_date),
                "expiry_date": str(p.expiry_date) if p.expiry_date else None,
                "completed_date": str(p.completed_date) if p.completed_date else None,
                "result_grade": p.result_grade,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in permits
        ]
    }


# ============================================
# ATTENDANCE VIEW
# ============================================

@router.get("/attendance")
async def get_attendance(
    date_val: Optional[date] = None,
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get attendance records (read-only view for registrar)."""
    target_date = date_val or date.today()
    
    query = select(Attendance).where(Attendance.date == target_date)
    
    if group_id:
        query = query.join(Student, Attendance.student_id == Student.id).where(Student.group_id == group_id)
    
    if status_filter:
        query = query.where(Attendance.status == status_filter)
    
    count_q = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_q) or 0
    
    query = query.order_by(Attendance.id).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    
    items = []
    for a in records:
        student = await db.get(Student, a.student_id)
        items.append({
            "id": a.id,
            "student_id": a.student_id,
            "student_name": student.name if student else "Noma'lum",
            "group_name": student.group.name if student and student.group else None,
            "date": str(a.date),
            "status": a.status.value if hasattr(a.status, 'value') else a.status,
            "subject": a.subject,
            "lesson_number": a.lesson_number,
            "check_in_time": str(a.check_in_time) if a.check_in_time else None,
            "late_minutes": a.late_minutes,
            "marked_by": a.marked_by_name if hasattr(a, 'marked_by_name') else None,
        })
    
    # Stats for the day
    day_stats = {
        "total": total,
        "present": sum(1 for i in items if i["status"] == "present"),
        "absent": sum(1 for i in items if i["status"] == "absent"),
        "late": sum(1 for i in items if i["status"] == "late"),
        "excused": sum(1 for i in items if i["status"] == "excused"),
    }
    
    return {"items": items, "total": total, "stats": day_stats, "date": str(target_date)}


# ============================================
# NB PERMITS
# ============================================

@router.get("/permits")
async def get_permits(
    status_filter: Optional[str] = None,
    student_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get all NB permits."""
    query = select(NBPermit)
    
    if status_filter:
        query = query.where(NBPermit.status == status_filter)
    
    if student_id:
        query = query.where(NBPermit.student_id == student_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                NBPermit.permit_code.ilike(search_filter),
                NBPermit.subject_name.ilike(search_filter),
            )
        )
    
    count_q = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_q) or 0
    
    query = query.order_by(NBPermit.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    permits = result.scalars().all()
    
    items = []
    for p in permits:
        items.append({
            "id": p.id,
            "permit_code": p.permit_code,
            "student_id": p.student_id,
            "student_name": p.student.name if p.student else None,
            "student_sid": p.student.student_id if p.student else None,
            "group_name": p.group.name if p.group else None,
            "subject_name": p.subject_name,
            "semester": p.semester,
            "academic_year": p.academic_year,
            "nb_type": p.nb_type,
            "reason": p.reason,
            "teacher_id": p.teacher_id,
            "teacher_name": p.teacher_name,
            "issued_by_name": p.issued_by_name,
            "issue_date": str(p.issue_date),
            "expiry_date": str(p.expiry_date) if p.expiry_date else None,
            "completed_date": str(p.completed_date) if p.completed_date else None,
            "status": p.status if isinstance(p.status, str) else p.status.value,
            "result_grade": p.result_grade,
            "teacher_notes": p.teacher_notes,
            "registrar_notes": p.registrar_notes,
            "print_count": p.print_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.post("/permits")
async def create_permit(
    data: NBPermitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Create a new NB permit."""
    # Verify student exists
    student = await db.get(Student, data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    
    # Generate permit code and verification hash
    permit_code = NBPermit.generate_permit_code()
    today = date.today()
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
        "message": "Ruxsatnoma muvaffaqiyatli yaratildi"
    }


@router.put("/permits/{permit_id}")
async def update_permit(
    permit_id: int,
    data: NBPermitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Update permit (registrar can change status, notes)."""
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")
    
    if data.status:
        permit.status = data.status
        if data.status in [PermitStatus.APPROVED]:
            permit.completed_date = date.today()
    if data.result_grade is not None:
        permit.result_grade = data.result_grade
    if data.teacher_notes is not None:
        permit.teacher_notes = data.teacher_notes
    if data.registrar_notes is not None:
        permit.registrar_notes = data.registrar_notes
    
    await db.commit()
    return {"message": "Ruxsatnoma yangilandi"}


@router.delete("/permits/{permit_id}")
async def delete_permit(
    permit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Delete/cancel permit."""
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")
    
    # Only allow deleting if status is issued or cancelled
    if permit.status not in [PermitStatus.ISSUED, PermitStatus.CANCELLED]:
        permit.status = PermitStatus.CANCELLED
        await db.commit()
        return {"message": "Ruxsatnoma bekor qilindi"}
    
    await db.delete(permit)
    await db.commit()
    return {"message": "Ruxsatnoma o'chirildi"}


# ============================================
# PERMIT CHECK (RECEIPT) - for printing
# ============================================

@router.get("/permits/{permit_id}/check")
async def get_permit_check(
    permit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar_or_teacher)
):
    """Get permit check/receipt data for printing. Increments print count."""
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")
    
    # Verify integrity
    is_valid = permit.verify()
    
    student = await db.get(Student, permit.student_id)
    
    # Increment print count
    permit.print_count += 1
    await db.commit()
    
    return {
        "permit_code": permit.permit_code,
        "is_valid": is_valid,
        "student": {
            "name": student.name if student else "Noma'lum",
            "student_id": student.student_id if student else None,
            "group_name": student.group.name if student and student.group else None,
            "faculty": student.group.faculty if student and student.group else None,
        },
        "subject_name": permit.subject_name,
        "semester": permit.semester,
        "academic_year": permit.academic_year,
        "nb_type": permit.nb_type,
        "reason": permit.reason,
        "teacher_name": permit.teacher_name,
        "issued_by_name": permit.issued_by_name,
        "issue_date": str(permit.issue_date),
        "expiry_date": str(permit.expiry_date) if permit.expiry_date else None,
        "completed_date": str(permit.completed_date) if permit.completed_date else None,
        "status": permit.status if isinstance(permit.status, str) else permit.status.value,
        "result_grade": permit.result_grade,
        "teacher_notes": permit.teacher_notes,
        "print_count": permit.print_count,
        "verification_hash": permit.verification_hash[:16] + "...",
    }


# ============================================
# VERIFY PERMIT (PUBLIC - by code)
# ============================================

@router.get("/verify/{permit_code}")
async def verify_permit(
    permit_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify permit by code (can be used publicly for validation)."""
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
        "subject_name": permit.subject_name,
        "status": permit.status if isinstance(permit.status, str) else permit.status.value,
        "issue_date": str(permit.issue_date),
        "result_grade": permit.result_grade,
        "is_approved": permit.status == PermitStatus.APPROVED or permit.status == "approved",
    }


# ============================================
# TEACHER PERMITS (permits assigned to current teacher)
# ============================================

@router.get("/teacher-permits")
async def get_teacher_permits(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get permits assigned to current teacher."""
    if current_user.role not in [UserRole.TEACHER, UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat o'qituvchilar uchun")
    
    query = select(NBPermit).where(NBPermit.teacher_id == current_user.id)
    
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
            "student_name": p.student.name if p.student else None,
            "student_sid": p.student.student_id if p.student else None,
            "group_name": p.group.name if p.group else None,
            "subject_name": p.subject_name,
            "semester": p.semester,
            "nb_type": p.nb_type,
            "status": p.status if isinstance(p.status, str) else p.status.value,
            "issue_date": str(p.issue_date),
            "expiry_date": str(p.expiry_date) if p.expiry_date else None,
            "result_grade": p.result_grade,
            "teacher_notes": p.teacher_notes,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    
    return {"items": items, "total": len(items)}


@router.put("/teacher-permits/{permit_id}")
async def teacher_update_permit(
    permit_id: int,
    data: NBPermitTeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Teacher updates permit status (approve/reject)."""
    if current_user.role not in [UserRole.TEACHER, UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat o'qituvchilar uchun")
    
    permit = await db.get(NBPermit, permit_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Ruxsatnoma topilmadi")
    
    if permit.teacher_id != current_user.id and current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Bu ruxsatnoma sizga tegishli emas")
    
    if data.status in ["approved", PermitStatus.APPROVED]:
        permit.status = PermitStatus.APPROVED
        permit.completed_date = date.today()
    elif data.status in ["rejected", PermitStatus.REJECTED]:
        permit.status = PermitStatus.REJECTED
    else:
        raise HTTPException(status_code=400, detail="Noto'g'ri status. Faqat: approved, rejected")
    
    if data.result_grade is not None:
        permit.result_grade = data.result_grade
    if data.teacher_notes is not None:
        permit.teacher_notes = data.teacher_notes
    
    await db.commit()
    
    return {"message": f"Ruxsatnoma {data.status} qilindi", "status": permit.status}


# ============================================
# GROUPS (for dropdown)
# ============================================

@router.get("/groups")
async def get_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get all active groups."""
    result = await db.execute(
        select(Group).where(Group.is_active == True).order_by(Group.name)
    )
    groups = result.scalars().all()
    
    return {
        "items": [
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
# TEACHERS (for dropdown)
# ============================================

@router.get("/teachers")
async def get_teachers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_registrar)
):
    """Get all teachers for permit assignment."""
    result = await db.execute(
        select(User).where(
            and_(User.role == UserRole.TEACHER, User.is_active == True)
        ).order_by(User.name)
    )
    teachers = result.scalars().all()
    
    return {
        "items": [
            {"id": t.id, "name": t.name}
            for t in teachers
        ]
    }


# ============================================
# STUDENT: My NB Permits (read-only)
# ============================================

@router.get("/my-permits")
async def get_my_permits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get NB permits for current student (read-only)."""
    if current_user.role not in [UserRole.STUDENT, UserRole.LEADER, UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat talabalar uchun")

    # Find student by user_id
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        return {"items": [], "total": 0}

    # Get permits for this student
    query = select(NBPermit).where(
        NBPermit.student_id == student.id
    ).order_by(NBPermit.created_at.desc())
    result = await db.execute(query)
    permits = result.scalars().all()

    items = []
    for p in permits:
        items.append({
            "id": p.id,
            "permit_code": p.permit_code,
            "subject_name": p.subject_name,
            "semester": p.semester,
            "academic_year": p.academic_year,
            "nb_type": p.nb_type,
            "reason": p.reason,
            "teacher_name": p.teacher_name,
            "issued_by_name": p.issued_by_name,
            "issue_date": str(p.issue_date),
            "expiry_date": str(p.expiry_date) if p.expiry_date else None,
            "completed_date": str(p.completed_date) if p.completed_date else None,
            "status": p.status if isinstance(p.status, str) else p.status.value,
            "result_grade": p.result_grade,
            "teacher_notes": p.teacher_notes,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {"items": items, "total": len(items)}


# ============================================
# LEADER: Group NB Permits (read-only)
# ============================================

@router.get("/group-permits")
async def get_group_permits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get NB permits for leader's group students (read-only)."""
    if current_user.role not in [UserRole.LEADER, UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat guruh sardorlari uchun")

    # Find student record for leader
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    leader_student = result.scalar_one_or_none()
    if not leader_student or not leader_student.group_id:
        return {"items": [], "total": 0}

    # Find group where this student is leader
    group_result = await db.execute(
        select(Group).where(
            and_(Group.leader_id == leader_student.id, Group.is_active == True)
        )
    )
    group = group_result.scalar_one_or_none()
    if not group:
        # Fallback: use student's own group
        group = await db.get(Group, leader_student.group_id)
    if not group:
        return {"items": [], "total": 0}

    # Get all students in this group
    students_result = await db.execute(
        select(Student.id, Student.name, Student.student_id).where(
            Student.group_id == group.id
        )
    )
    students_map = {row[0]: {"name": row[1], "student_id": row[2]} for row in students_result.all()}
    student_ids = list(students_map.keys())

    if not student_ids:
        return {"items": [], "total": 0, "group_name": group.name}

    # Get permits for all group students
    query = select(NBPermit).where(
        NBPermit.student_id.in_(student_ids)
    ).order_by(NBPermit.created_at.desc())
    result = await db.execute(query)
    permits = result.scalars().all()

    items = []
    for p in permits:
        s_info = students_map.get(p.student_id, {})
        items.append({
            "id": p.id,
            "permit_code": p.permit_code,
            "student_name": s_info.get("name", "Noma'lum"),
            "student_sid": s_info.get("student_id"),
            "subject_name": p.subject_name,
            "semester": p.semester,
            "academic_year": p.academic_year,
            "nb_type": p.nb_type,
            "reason": p.reason,
            "teacher_name": p.teacher_name,
            "issued_by_name": p.issued_by_name,
            "issue_date": str(p.issue_date),
            "expiry_date": str(p.expiry_date) if p.expiry_date else None,
            "completed_date": str(p.completed_date) if p.completed_date else None,
            "status": p.status if isinstance(p.status, str) else p.status.value,
            "result_grade": p.result_grade,
            "teacher_notes": p.teacher_notes,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {"items": items, "total": len(items), "group_name": group.name}
