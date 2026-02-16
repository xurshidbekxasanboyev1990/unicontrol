"""
UniControl - Mobile Tournaments Routes
========================================
Tournament endpoints for mobile app.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.tournament import Tournament, TournamentRegistration
from app.models.user import User
from app.models.student import Student
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("")
async def get_tournaments(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List tournaments for mobile."""
    query = select(Tournament)

    if status_filter:
        query = query.where(Tournament.status == status_filter)
    if search:
        query = query.where(Tournament.name.ilike(f"%{search}%"))

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Tournament.start_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tournaments = result.scalars().all()

    # Check registrations for current user
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()

    my_tournament_ids = set()
    if student:
        regs = await db.execute(
            select(TournamentRegistration.tournament_id).where(
                TournamentRegistration.student_id == student.id
            )
        )
        my_tournament_ids = {row[0] for row in regs.fetchall()}

    items = []
    for t in tournaments:
        # Count registrations
        reg_count_res = await db.execute(
            select(func.count(TournamentRegistration.id)).where(
                TournamentRegistration.tournament_id == t.id
            )
        )
        reg_count = reg_count_res.scalar() or 0

        items.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "subject_id": t.subject_id if hasattr(t, "subject_id") else None,
            "subject_name": t.subject_name if hasattr(t, "subject_name") else None,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "end_date": t.end_date.isoformat() if t.end_date else None,
            "registration_deadline": t.registration_deadline.isoformat() if hasattr(t, "registration_deadline") and t.registration_deadline else None,
            "participant_count": reg_count,
            "max_participants": t.max_participants if hasattr(t, "max_participants") else 0,
            "prize": t.prize if hasattr(t, "prize") else None,
            "rules": t.rules if hasattr(t, "rules") else None,
            "image_url": t.image_url if hasattr(t, "image_url") else None,
            "status": t.status,
            "is_registered": t.id in my_tournament_ids,
            "is_active": t.is_active if hasattr(t, "is_active") else True,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{tournament_id}")
async def get_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tournament detail."""
    result = await db.execute(
        select(Tournament).where(Tournament.id == tournament_id)
    )
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")

    # Check registration
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    is_registered = False
    if student:
        reg = await db.execute(
            select(TournamentRegistration).where(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.student_id == student.id,
            )
        )
        is_registered = reg.scalar_one_or_none() is not None

    reg_count = (await db.execute(
        select(func.count(TournamentRegistration.id)).where(
            TournamentRegistration.tournament_id == tournament_id
        )
    )).scalar() or 0

    return {
        "id": tournament.id,
        "name": tournament.name,
        "description": tournament.description,
        "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
        "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
        "participant_count": reg_count,
        "max_participants": tournament.max_participants if hasattr(tournament, "max_participants") else 0,
        "status": tournament.status,
        "is_registered": is_registered,
        "created_at": tournament.created_at.isoformat() if tournament.created_at else None,
    }


@router.post("/{tournament_id}/register")
async def register_for_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Register for a tournament."""
    result = await db.execute(
        select(Tournament).where(Tournament.id == tournament_id)
    )
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")

    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba profili topilmadi")

    # Check existing
    existing = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.tournament_id == tournament_id,
            TournamentRegistration.student_id == student.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Allaqachon ro'yxatdan o'tgansiz")

    # Check max participants
    if hasattr(tournament, "max_participants") and tournament.max_participants > 0:
        count = (await db.execute(
            select(func.count(TournamentRegistration.id)).where(
                TournamentRegistration.tournament_id == tournament_id
            )
        )).scalar() or 0
        if count >= tournament.max_participants:
            raise HTTPException(status_code=400, detail="Ishtirokchilar soni to'lgan")

    reg = TournamentRegistration(
        tournament_id=tournament_id,
        student_id=student.id,
    )
    db.add(reg)
    await db.commit()

    return {"message": "Turnirga muvaffaqiyatli ro'yxatdan o'tdingiz"}


@router.delete("/{tournament_id}/unregister")
async def unregister_from_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Unregister from a tournament."""
    student_res = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba profili topilmadi")

    result = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.tournament_id == tournament_id,
            TournamentRegistration.student_id == student.id,
        )
    )
    reg = result.scalar_one_or_none()
    if not reg:
        raise HTTPException(status_code=404, detail="Ro'yxatdan o'tilmagan")

    await db.delete(reg)
    await db.commit()

    return {"message": "Turnirdan chiqarildi"}
