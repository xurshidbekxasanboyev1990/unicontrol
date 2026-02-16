"""
UniControl - Mobile Clubs Routes
=================================
Club endpoints for mobile app.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.club import Club, ClubMember
from app.models.user import User
from app.models.student import Student
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("")
async def get_clubs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List clubs for mobile."""
    query = select(Club)

    if active_only:
        query = query.where(Club.is_active == True)
    if category:
        query = query.where(Club.category == category)
    if search:
        query = query.where(Club.name.ilike(f"%{search}%"))

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    clubs = result.scalars().all()

    # Check membership for current user
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()

    my_club_ids = set()
    if student:
        memberships = await db.execute(
            select(ClubMember.club_id).where(ClubMember.student_id == student.id)
        )
        my_club_ids = {row[0] for row in memberships.fetchall()}

    items = []
    for c in clubs:
        items.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "category": c.category,
            "image_url": c.image_url if hasattr(c, "image_url") else None,
            "leader_id": c.leader_id if hasattr(c, "leader_id") else None,
            "leader_name": c.leader_name if hasattr(c, "leader_name") else None,
            "member_count": c.members_count if hasattr(c, "members_count") else 0,
            "max_members": c.max_members if hasattr(c, "max_members") else 0,
            "schedule": c.schedule if hasattr(c, "schedule") else None,
            "location": c.location if hasattr(c, "location") else None,
            "is_active": c.is_active,
            "is_joined": c.id in my_club_ids,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{club_id}")
async def get_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get club detail."""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")

    # Check membership
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    is_joined = False
    if student:
        mem = await db.execute(
            select(ClubMember).where(
                ClubMember.club_id == club_id,
                ClubMember.student_id == student.id,
            )
        )
        is_joined = mem.scalar_one_or_none() is not None

    return {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "category": club.category,
        "image_url": club.image_url if hasattr(club, "image_url") else None,
        "leader_id": club.leader_id if hasattr(club, "leader_id") else None,
        "leader_name": club.leader_name if hasattr(club, "leader_name") else None,
        "member_count": club.members_count if hasattr(club, "members_count") else 0,
        "max_members": club.max_members if hasattr(club, "max_members") else 0,
        "schedule": club.schedule if hasattr(club, "schedule") else None,
        "location": club.location if hasattr(club, "location") else None,
        "is_active": club.is_active,
        "is_joined": is_joined,
        "created_at": club.created_at.isoformat() if club.created_at else None,
    }


@router.post("/{club_id}/join")
async def join_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Join a club."""
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()
    if not club:
        raise HTTPException(status_code=404, detail="To'garak topilmadi")
    if not club.is_active:
        raise HTTPException(status_code=400, detail="To'garak faol emas")

    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba profili topilmadi")

    # Check max members
    if hasattr(club, "max_members") and club.max_members > 0:
        current_count = club.members_count if hasattr(club, "members_count") else 0
        if current_count >= club.max_members:
            raise HTTPException(status_code=400, detail="To'garakda joy qolmadi")

    # Check existing
    existing = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.student_id == student.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Allaqachon a'zo")

    member = ClubMember(club_id=club_id, student_id=student.id)
    db.add(member)
    if hasattr(club, "members_count"):
        club.members_count += 1
    await db.commit()

    return {"message": "To'garakka muvaffaqiyatli qo'shildingiz"}


@router.delete("/{club_id}/leave")
async def leave_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Leave a club."""
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba profili topilmadi")

    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.student_id == student.id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Siz bu to'garak a'zosi emassiz")

    await db.delete(member)

    club_res = await db.execute(select(Club).where(Club.id == club_id))
    club = club_res.scalar_one_or_none()
    if club and hasattr(club, "members_count") and club.members_count > 0:
        club.members_count -= 1

    await db.commit()

    return {"message": "To'garakdan chiqdingiz"}
