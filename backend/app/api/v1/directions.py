"""
Direction (Yo'nalish) API Routes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.subject import Direction, DirectionSubject, Subject
from app.models.user import User
from app.schemas.subject import (
    DirectionCreate,
    DirectionUpdate,
    DirectionResponse,
    DirectionListResponse,
    DirectionSubjectUpdate,
)
from app.core.dependencies import get_current_active_user, require_admin

router = APIRouter()


@router.get("", response_model=DirectionListResponse)
async def get_directions(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yo'nalishlar ro'yxatini olish"""
    query = select(Direction)
    
    if is_active is not None:
        query = query.where(Direction.is_active == is_active)
    if search:
        query = query.where(
            Direction.name.ilike(f"%{search}%") | Direction.code.ilike(f"%{search}%")
        )
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    directions = result.scalars().all()
    
    return DirectionListResponse(
        items=[DirectionResponse.model_validate(d) for d in directions],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=DirectionResponse, status_code=status.HTTP_201_CREATED)
async def create_direction(
    data: DirectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yangi yo'nalish yaratish"""
    # Check unique code
    existing = await db.execute(select(Direction).where(Direction.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud")
    
    direction = Direction(**data.model_dump())
    db.add(direction)
    await db.commit()
    await db.refresh(direction)
    return direction


@router.get("/{direction_id}", response_model=DirectionResponse)
async def get_direction(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yo'nalish ma'lumotlarini olish"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    return direction


@router.put("/{direction_id}", response_model=DirectionResponse)
async def update_direction(
    direction_id: int,
    data: DirectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yo'nalishni yangilash"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    
    # Check code unique if changed
    if data.code and data.code != direction.code:
        existing = await db.execute(select(Direction).where(Direction.code == data.code))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(direction, field, value)
    
    await db.commit()
    await db.refresh(direction)
    return direction


@router.delete("/{direction_id}")
async def delete_direction(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yo'nalishni o'chirish"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    
    await db.delete(direction)
    await db.commit()
    return {"message": "Yo'nalish o'chirildi"}


@router.patch("/{direction_id}/toggle-status", response_model=DirectionResponse)
async def toggle_direction_status(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yo'nalish statusini o'zgartirish"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    
    direction.is_active = not direction.is_active
    await db.commit()
    await db.refresh(direction)
    return direction


@router.put("/{direction_id}/subjects")
async def update_direction_subjects(
    direction_id: int,
    data: DirectionSubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yo'nalish fanlarini yangilash"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    
    # Delete existing
    await db.execute(
        DirectionSubject.__table__.delete().where(
            DirectionSubject.direction_id == direction_id
        )
    )
    
    # Add new
    for subject_data in data.subjects:
        # Check subject exists
        subject_result = await db.execute(
            select(Subject).where(Subject.id == subject_data.subject_id)
        )
        if not subject_result.scalar_one_or_none():
            continue
        
        direction_subject = DirectionSubject(
            direction_id=direction_id,
            subject_id=subject_data.subject_id,
            semester=subject_data.semester,
            is_required=subject_data.is_required
        )
        db.add(direction_subject)
    
    await db.commit()
    return {"message": "Fanlar yangilandi"}


@router.get("/{direction_id}/subjects")
async def get_direction_subjects(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yo'nalish fanlarini olish"""
    result = await db.execute(select(Direction).where(Direction.id == direction_id))
    direction = result.scalar_one_or_none()
    if not direction:
        raise HTTPException(status_code=404, detail="Yo'nalish topilmadi")
    
    subjects_result = await db.execute(
        select(DirectionSubject, Subject)
        .join(Subject, DirectionSubject.subject_id == Subject.id)
        .where(DirectionSubject.direction_id == direction_id)
    )
    
    subjects = []
    for ds, subject in subjects_result.all():
        subjects.append({
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "semester": ds.semester,
            "is_required": ds.is_required
        })
    
    return subjects

