"""
Club (To'garak) API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.club import Club, ClubMember
from app.models.user import User
from app.schemas.club import (
    ClubCreate,
    ClubUpdate,
    ClubResponse,
    ClubListResponse,
    ClubMemberCreate,
    ClubMemberResponse,
)
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=ClubListResponse)
async def get_clubs(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garaklar ro'yxatini olish"""
    query = select(Club)
    
    if category:
        query = query.where(Club.category == category)
    if is_active is not None:
        query = query.where(Club.is_active == is_active)
    if search:
        query = query.where(Club.name.ilike(f"%{search}%"))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    clubs = result.scalars().all()
    
    return ClubListResponse(
        items=[ClubResponse.model_validate(c) for c in clubs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    data: ClubCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Yangi to'garak yaratish"""
    club = Club(**data.model_dump())
    db.add(club)
    await db.commit()
    await db.refresh(club)
    return club


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garak ma'lumotlarini olish"""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    return club


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    data: ClubUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garakni yangilash"""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(club, field, value)
    
    await db.commit()
    await db.refresh(club)
    return club


@router.delete("/{club_id}")
async def delete_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garakni o'chirish"""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    
    await db.delete(club)
    await db.commit()
    return {"message": "To'garak o'chirildi"}


@router.patch("/{club_id}/toggle-status", response_model=ClubResponse)
async def toggle_club_status(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garak statusini o'zgartirish"""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    
    club.is_active = not club.is_active
    await db.commit()
    await db.refresh(club)
    return club


# ============ Club Members ============

@router.post("/{club_id}/join", response_model=ClubMemberResponse)
async def join_club(
    club_id: int,
    student_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garakka a'zo bo'lish"""
    # Check club
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    
    if not club.is_active:
        raise HTTPException(status_code=400, detail="To'garak faol emas")
    
    if club.members_count >= club.max_members:
        raise HTTPException(status_code=400, detail="To'garakda joy qolmadi")
    
    # Check existing
    existing = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.student_id == student_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Allaqachon a'zo")
    
    member = ClubMember(club_id=club_id, student_id=student_id)
    db.add(member)
    club.members_count += 1
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{club_id}/leave")
async def leave_club(
    club_id: int,
    student_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'garakdan chiqish"""
    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.student_id == student_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="A'zo topilmadi")
    
    # Update count
    club_result = await db.execute(select(Club).where(Club.id == club_id))
    club = club_result.scalar_one_or_none()
    if club and club.members_count > 0:
        club.members_count -= 1
    
    await db.delete(member)
    await db.commit()
    return {"message": "To'garakdan chiqildi"}
