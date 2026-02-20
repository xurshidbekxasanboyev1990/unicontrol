"""
UniControl - Student Routes
===========================
Student management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import date, timedelta
from typing import Optional, List
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import extract, and_, or_, select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.student_service import StudentService
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
    StudentStats,
    PaymentUpdate,
)
from app.core.dependencies import get_current_active_user, require_leader, require_admin
from app.models.user import User
from app.models.student import Student
from app.models.group import Group
from app.config import TASHKENT_TZ

router = APIRouter()


@router.get("/faculties")
async def student_faculties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get distinct faculties and course years from actual DB data."""
    # Faculties
    fac_result = await db.execute(
        select(distinct(Group.faculty))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != ""))
        .order_by(Group.faculty)
    )
    faculties = [r[0] for r in fac_result.all() if r[0]]

    # Course years
    cy_result = await db.execute(
        select(distinct(Group.course_year))
        .where(and_(Group.is_active == True, Group.course_year.isnot(None)))
        .order_by(Group.course_year)
    )
    course_years = [r[0] for r in cy_result.all() if r[0]]

    # Faculty with student counts
    fac_counts_result = await db.execute(
        select(
            Group.faculty,
            func.count(Student.id).label('students_count')
        )
        .outerjoin(Student, and_(Student.group_id == Group.id, Student.is_active == True))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None), Group.faculty != ""))
        .group_by(Group.faculty)
        .order_by(Group.faculty)
    )
    faculty_counts = [
        {"name": r[0], "students_count": r[1] or 0}
        for r in fac_counts_result.all() if r[0]
    ]

    return {"faculties": faculties, "course_years": course_years, "faculty_counts": faculty_counts}


@router.get("", response_model=StudentListResponse)
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=50000),
    group_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_graduated: Optional[bool] = None,
    search: Optional[str] = None,
    faculty: Optional[str] = None,
    course_year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List students with pagination and filters.
    """
    service = StudentService(db)
    students, total = await service.list_students(
        page=page,
        page_size=page_size,
        group_id=group_id,
        is_active=is_active,
        is_graduated=is_graduated,
        search=search,
        faculty=faculty,
        course_year=course_year
    )
    
    return StudentListResponse(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new student.
    
    Requires admin role.
    """
    service = StudentService(db)
    student = await service.create(student_data)
    return StudentResponse.model_validate(student)


@router.get("/statistics", response_model=StudentStats)
async def get_statistics(
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get student statistics.
    
    Requires leader role.
    """
    service = StudentService(db)
    return await service.get_statistics(group_id)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student by ID.
    """
    service = StudentService(db)
    student = await service.get_by_id(student_id)
    if not student:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Student not found")
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Update student.
    
    Requires leader role.
    """
    service = StudentService(db)
    student = await service.update(student_id, student_data)
    return StudentResponse.model_validate(student)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete student.
    
    Requires admin role.
    """
    service = StudentService(db)
    await service.delete(student_id)
    return {"message": "Student deleted successfully"}


@router.post("/{student_id}/payment", response_model=StudentResponse)
async def add_payment(
    student_id: int,
    payment: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Add payment to student's contract.
    
    Requires admin role.
    """
    service = StudentService(db)
    student = await service.add_payment(student_id, payment.amount, payment.note)
    return StudentResponse.model_validate(student)


@router.post("/{student_id}/set-leader", response_model=StudentResponse)
async def set_as_leader(
    student_id: int,
    is_leader: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Set or unset student as group leader.
    
    Requires admin role.
    """
    service = StudentService(db)
    student = await service.set_leader(student_id, is_leader)
    return StudentResponse.model_validate(student)


@router.post("/{student_id}/graduate", response_model=StudentResponse)
async def mark_as_graduated(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Mark student as graduated.
    
    Requires admin role.
    """
    service = StudentService(db)
    student = await service.graduate(student_id)
    return StudentResponse.model_validate(student)


@router.get("/by-code/{student_code}", response_model=StudentResponse)
async def get_student_by_code(
    student_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student by student_id code.
    """
    service = StudentService(db)
    student = await service.get_by_student_id(student_code)
    if not student:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Student not found")
    return StudentResponse.model_validate(student)


@router.get("/group/{group_id}", response_model=list)
async def get_group_students(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students in a group.
    """
    service = StudentService(db)
    students = await service.get_group_students(group_id)
    return [StudentResponse.model_validate(s) for s in students]


@router.get("/birthdays/upcoming")
async def get_upcoming_birthdays(
    group_id: Optional[int] = Query(None, description="Filter by group"),
    days: int = Query(7, description="How many days ahead to check"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get students with birthdays today, tomorrow, and upcoming days.
    Returns students grouped by: today, tomorrow, upcoming.
    """
    from datetime import datetime
    now = datetime.now(TASHKENT_TZ)
    today = now.date()
    
    results = {"today": [], "tomorrow": [], "upcoming": []}
    
    # Build base query
    query = select(Student).where(Student.birth_date.isnot(None))
    if group_id:
        query = query.where(Student.group_id == group_id)
    
    result = await db.execute(query)
    students = result.scalars().all()
    
    for student in students:
        if not student.birth_date:
            continue
        
        bday_this_year = student.birth_date.replace(year=today.year)
        # Handle leap year edge case
        try:
            bday_this_year = student.birth_date.replace(year=today.year)
        except ValueError:
            # Feb 29 in non-leap year
            bday_this_year = date(today.year, 2, 28)
        
        delta = (bday_this_year - today).days
        
        # If birthday already passed this year, check next year
        if delta < 0:
            try:
                bday_this_year = student.birth_date.replace(year=today.year + 1)
            except ValueError:
                bday_this_year = date(today.year + 1, 2, 28)
            delta = (bday_this_year - today).days
        
        if delta > days:
            continue
        
        age = today.year - student.birth_date.year
        if delta > 0:
            age = bday_this_year.year - student.birth_date.year
        
        student_data = {
            "id": student.id,
            "name": student.name or student.full_name or "Ism kiritilmagan",
            "student_id": student.student_id,
            "group_id": student.group_id,
            "birth_date": student.birth_date.isoformat(),
            "user_id": student.user_id,
            "age": age,
            "days_until": delta,
            "avatar": student.avatar
        }
        
        if delta == 0:
            results["today"].append(student_data)
        elif delta == 1:
            results["tomorrow"].append(student_data)
        else:
            student_data["birthday_date"] = bday_this_year.isoformat()
            results["upcoming"].append(student_data)
    
    # Sort upcoming by days_until
    results["upcoming"].sort(key=lambda x: x["days_until"])
    
    return results
