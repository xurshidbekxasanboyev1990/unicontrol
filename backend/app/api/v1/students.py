"""
UniControl - Student Routes
===========================
Student management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
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

router = APIRouter()


@router.get("", response_model=StudentListResponse)
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=20000),
    group_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_graduated: Optional[bool] = None,
    search: Optional[str] = None,
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
        search=search
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
