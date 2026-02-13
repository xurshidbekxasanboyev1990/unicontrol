"""
Tournament (Musobaqa) API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from loguru import logger

from app.database import get_db
from app.models.tournament import Tournament, TournamentRegistration
from app.models.user import User
from app.models.student import Student
from app.models.group import Group
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.schemas.tournament import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentListResponse,
    TournamentRegister,
    TournamentRegistrationResponse,
)
from app.core.dependencies import get_current_active_user, require_admin
from app.config import today_tashkent

router = APIRouter()


@router.get("", response_model=TournamentListResponse)
async def get_tournaments(
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Musobaqalar ro'yxatini olish"""
    query = select(Tournament)
    
    if category:
        query = query.where(Tournament.category == category)
    if status_filter:
        query = query.where(Tournament.status == status_filter)
    if search:
        query = query.where(Tournament.name.ilike(f"%{search}%"))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Order by start_date desc
    query = query.order_by(Tournament.start_date.desc())
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tournaments = result.scalars().all()
    
    # Build response with registration counts
    tournament_items = []
    for t in tournaments:
        count_result = await db.execute(
            select(func.count(TournamentRegistration.id)).where(
                TournamentRegistration.tournament_id == t.id
            )
        )
        reg_count = count_result.scalar() or 0
        t_dict = {c.name: getattr(t, c.name) for c in t.__table__.columns}
        t_dict["registrations_count"] = reg_count
        tournament_items.append(TournamentResponse(**t_dict))
    
    return TournamentListResponse(
        items=tournament_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/my-registrations")
async def get_my_registrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Joriy talabaning barcha ro'yxatdan o'tgan turnirlarini olish"""
    # Find student by user_id
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        return []
    
    result = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.student_id == student.id
        )
    )
    registrations = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "tournament_id": r.tournament_id,
            "student_id": r.student_id,
            "status": r.status,
            "registered_at": r.registered_at.isoformat() if r.registered_at else None,
        }
        for r in registrations
    ]


@router.post("", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Yangi musobaqa yaratish"""
    tournament = Tournament(**data.model_dump())
    db.add(tournament)
    await db.commit()
    await db.refresh(tournament)
    return tournament


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Musobaqa ma'lumotlarini olish"""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    # Count registrations
    count_result = await db.execute(
        select(func.count(TournamentRegistration.id)).where(
            TournamentRegistration.tournament_id == tournament_id
        )
    )
    reg_count = count_result.scalar() or 0
    t_dict = {c.name: getattr(tournament, c.name) for c in tournament.__table__.columns}
    t_dict["registrations_count"] = reg_count
    return TournamentResponse(**t_dict)


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    data: TournamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Musobaqani yangilash"""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tournament, field, value)
    
    await db.commit()
    await db.refresh(tournament)
    return tournament


@router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Musobaqani o'chirish"""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    await db.delete(tournament)
    await db.commit()
    return {"message": "Musobaqa o'chirildi"}


@router.patch("/{tournament_id}/toggle-status", response_model=TournamentResponse)
async def toggle_tournament_status(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Musobaqa statusini o'zgartirish"""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    # Cycle through statuses
    status_cycle = ["upcoming", "pending", "active", "completed", "cancelled"]
    current_index = status_cycle.index(tournament.status) if tournament.status in status_cycle else 0
    tournament.status = status_cycle[(current_index + 1) % len(status_cycle)]
    
    await db.commit()
    await db.refresh(tournament)
    return tournament


# ============ Registration ============

@router.post("/{tournament_id}/register", response_model=TournamentRegistrationResponse)
async def register_for_tournament(
    tournament_id: int,
    data: TournamentRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Musobaqaga ro'yxatdan o'tish"""
    # Check tournament
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    if tournament.status not in ["pending", "active", "upcoming"]:
        raise HTTPException(status_code=400, detail="Musobaqaga ro'yxatdan o'tish mumkin emas")
    
    if tournament.registration_deadline and today_tashkent() > tournament.registration_deadline:
        raise HTTPException(status_code=400, detail="Ro'yxatdan o'tish muddati tugagan")
    
    # Count current registrations
    reg_count_result = await db.execute(
        select(func.count(TournamentRegistration.id)).where(
            TournamentRegistration.tournament_id == tournament_id
        )
    )
    current_count = reg_count_result.scalar() or 0
    if tournament.max_participants and current_count >= tournament.max_participants:
        raise HTTPException(status_code=400, detail="Musobaqada joy qolmadi")
    
    # Validate student exists
    student_check = await db.execute(
        select(Student).where(Student.id == data.student_id)
    )
    if not student_check.scalar_one_or_none():
        # Try to find student by user_id (frontend may send user.id instead of student.id)
        student_by_user = await db.execute(
            select(Student).where(Student.user_id == data.student_id)
        )
        found_student = student_by_user.scalar_one_or_none()
        if found_student:
            data.student_id = found_student.id
        else:
            raise HTTPException(status_code=400, detail="Talaba topilmadi. Faqat talabalar turnirga ro'yxatdan o'tishi mumkin.")
    
    # Check existing
    existing = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.tournament_id == tournament_id,
            TournamentRegistration.student_id == data.student_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Siz bu turnirga allaqachon ro'yxatdan o'tgansiz")
    
    registration = TournamentRegistration(
        tournament_id=tournament_id,
        student_id=data.student_id
    )
    db.add(registration)
    await db.commit()
    await db.refresh(registration)
    
    # Send notification to student
    try:
        student_result = await db.execute(
            select(Student).where(Student.id == data.student_id)
        )
        student = student_result.scalar_one_or_none()
        if student and student.user_id:
            notification = Notification(
                user_id=student.user_id,
                title="Turnirga ro'yxatdan o'tdingiz ✅",
                message=f"Siz \"{tournament.name}\" turnirga muvaffaqiyatli ro'yxatdan o'tdingiz. Tasdiqlashni kuting.",
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                sender_id=current_user.id,
            )
            db.add(notification)
            await db.commit()
    except Exception as e:
        logger.warning(f"Tournament registration notification error: {e}")
    
    return registration


@router.patch("/{tournament_id}/registrations/{registration_id}/status")
async def update_registration_status(
    tournament_id: int,
    registration_id: int,
    new_status: str = Query(..., alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Ro'yxatdan o'tish statusini yangilash (tasdiqlash/rad etish)"""
    # Check tournament
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    # Check registration
    reg_result = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.id == registration_id,
            TournamentRegistration.tournament_id == tournament_id
        )
    )
    registration = reg_result.scalar_one_or_none()
    if not registration:
        raise HTTPException(status_code=404, detail="Ro'yxat topilmadi")
    
    old_status = registration.status
    registration.status = new_status
    await db.commit()
    await db.refresh(registration)
    
    # Send notification to student
    try:
        student_result = await db.execute(
            select(Student).where(Student.id == registration.student_id)
        )
        student = student_result.scalar_one_or_none()
        if student and student.user_id:
            if new_status in ("confirmed", "approved"):
                title = "Turnir arizangiz tasdiqlandi ✅"
                message = f"\"{tournament.name}\" turnirga arizangiz tasdiqlandi! Turnir boshlanish sanasi: {tournament.start_date or 'belgilanmagan'}. Omad!"
                priority = NotificationPriority.HIGH
            elif new_status == "rejected":
                title = "Turnir arizangiz rad etildi ❌"
                message = f"\"{tournament.name}\" turnirga arizangiz rad etildi. Qo'shimcha ma'lumot uchun admin bilan bog'laning."
                priority = NotificationPriority.HIGH
            elif new_status == "cancelled":
                title = "Turnir arizangiz bekor qilindi"
                message = f"\"{tournament.name}\" turniriga arizangiz bekor qilindi."
                priority = NotificationPriority.NORMAL
            else:
                title = "Turnir arizangiz yangilandi"
                message = f"\"{tournament.name}\" turniridagi arizangiz statusi o'zgartirildi: {new_status}"
                priority = NotificationPriority.NORMAL
            
            notification = Notification(
                user_id=student.user_id,
                title=title,
                message=message,
                type=NotificationType.INFO,
                priority=priority,
                sender_id=current_user.id,
            )
            db.add(notification)
            await db.commit()
    except Exception as e:
        logger.warning(f"Tournament status notification error: {e}")
    
    return {
        "id": registration.id,
        "tournament_id": registration.tournament_id,
        "student_id": registration.student_id,
        "status": registration.status,
        "registered_at": registration.registered_at.isoformat() if registration.registered_at else None,
    }


@router.post("/{tournament_id}/unregister")
async def unregister_from_tournament(
    tournament_id: int,
    data: TournamentRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Musobaqadan ro'yxatdan chiqish"""
    student_id = data.student_id
    
    # Also try user_id -> student_id mapping
    student_check = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    if not student_check.scalar_one_or_none():
        student_by_user = await db.execute(
            select(Student).where(Student.user_id == student_id)
        )
        found_student = student_by_user.scalar_one_or_none()
        if found_student:
            student_id = found_student.id
    
    result = await db.execute(
        select(TournamentRegistration).where(
            TournamentRegistration.tournament_id == tournament_id,
            TournamentRegistration.student_id == student_id
        )
    )
    registration = result.scalar_one_or_none()
    if not registration:
        raise HTTPException(status_code=404, detail="Ro'yxat topilmadi")
    
    await db.delete(registration)
    await db.commit()
    return {"message": "Ro'yxatdan chiqildi"}


@router.get("/{tournament_id}/participants")
async def get_tournament_participants(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Musobaqa ishtirokchilarini olish - talaba ma'lumotlari bilan"""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Musobaqa topilmadi")
    
    registrations = await db.execute(
        select(
            TournamentRegistration,
            Student.name.label("student_name"),
            Student.student_id.label("student_code"),
            Student.phone.label("student_phone"),
            Group.name.label("group_name")
        )
        .join(Student, TournamentRegistration.student_id == Student.id, isouter=True)
        .join(Group, Student.group_id == Group.id, isouter=True)
        .where(TournamentRegistration.tournament_id == tournament_id)
        .order_by(TournamentRegistration.registered_at)
    )
    
    items = []
    for row in registrations.all():
        reg = row[0]
        items.append({
            "id": reg.id,
            "tournament_id": reg.tournament_id,
            "student_id": reg.student_id,
            "registered_at": reg.registered_at.isoformat() if reg.registered_at else None,
            "status": reg.status,
            "position": reg.position,
            "score": reg.score,
            "student_name": row.student_name or "Noma'lum",
            "student_code": row.student_code or "",
            "student_phone": row.student_phone or "",
            "group_name": row.group_name or ""
        })
    
    return items

