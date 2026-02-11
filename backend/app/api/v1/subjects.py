"""
Subject API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.subject import Subject
from app.models.user import User
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectListResponse,
)
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=SubjectListResponse)
async def get_subjects(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fanlar ro'yxatini olish"""
    query = select(Subject)
    
    if search:
        query = query.where(
            Subject.name.ilike(f"%{search}%") | Subject.code.ilike(f"%{search}%")
        )
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    subjects = result.scalars().all()
    
    return SubjectListResponse(
        items=[SubjectResponse.model_validate(s) for s in subjects],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yangi fan yaratish"""
    # Check unique code
    existing = await db.execute(select(Subject).where(Subject.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud")
    
    subject = Subject(**data.model_dump())
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return subject


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fan ma'lumotlarini olish"""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Fan topilmadi")
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fanni yangilash"""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Fan topilmadi")
    
    # Check code unique if changed
    if data.code and data.code != subject.code:
        existing = await db.execute(select(Subject).where(Subject.code == data.code))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    
    await db.commit()
    await db.refresh(subject)
    return subject


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fanni o'chirish"""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Fan topilmadi")
    
    await db.delete(subject)
    await db.commit()
    return {"message": "Fan o'chirildi"}
