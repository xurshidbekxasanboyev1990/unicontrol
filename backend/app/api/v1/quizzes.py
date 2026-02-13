"""
UniControl - Quiz API Routes
==============================
Endpoints for quiz/flashcard management (Quizlet-style).
Students and leaders can create, share, and take quizzes within their group.
Requires group subscription: plus, pro, or unlimited.

Author: UniControl Team
Version: 1.1.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.quiz_service import QuizService
from app.schemas.quiz import (
    QuizSetCreate, QuizSetUpdate, QuizSetResponse, QuizSetListResponse,
    QuizCardCreate, QuizCardUpdate, QuizCardResponse,
    QuizResultCreate, QuizResultResponse,
)
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.group import Group
from app.models.subscription import (
    GroupSubscription, SubscriptionStatus, SubscriptionPlanType,
    SubscriptionSettings,
)
from app.config import today_tashkent

router = APIRouter()

# ============ Subscription Plans That Allow Quizzes ============
QUIZ_ALLOWED_PLANS = {
    SubscriptionPlanType.PLUS.value,
    SubscriptionPlanType.PRO.value,
    SubscriptionPlanType.UNLIMITED.value,
}


async def _check_quiz_subscription(db: AsyncSession, user_id: int, user_role: str):
    """
    Check if user's group has plus/pro/unlimited subscription.
    Superadmin and admin bypass the check.
    Raises HTTPException 403 if subscription is insufficient.
    """
    # Admins and superadmins bypass subscription check
    if user_role in ("admin", "superadmin"):
        return

    # Find student's group
    result = await db.execute(
        select(Student).where(Student.user_id == user_id)
    )
    student = result.scalar_one_or_none()
    if not student or not student.group_id:
        raise HTTPException(
            status_code=403,
            detail="quiz_no_group"
        )

    today = today_tashkent()

    # Check active group subscription
    result = await db.execute(
        select(GroupSubscription).where(
            GroupSubscription.group_id == student.group_id,
            GroupSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value,
            ]),
            GroupSubscription.end_date >= today,
        ).order_by(GroupSubscription.end_date.desc())
    )
    sub = result.scalar_one_or_none()

    if sub and sub.plan_type in QUIZ_ALLOWED_PLANS:
        return  # Access granted

    # Check global trial period (trial gives access)
    settings_result = await db.execute(select(SubscriptionSettings).limit(1))
    settings = settings_result.scalar_one_or_none()
    if settings and settings.trial_end_date and today <= settings.trial_end_date:
        return  # Trial period — access granted

    raise HTTPException(
        status_code=403,
        detail="quiz_subscription_required"
    )


def _set_to_response(qs) -> dict:
    """Convert QuizSet ORM to response dict."""
    return {
        "id": qs.id,
        "title": qs.title,
        "description": qs.description,
        "subject": qs.subject,
        "is_public": qs.is_public,
        "color": qs.color,
        "creator_id": qs.creator_id,
        "group_id": qs.group_id,
        "cards_count": qs.cards_count or 0,
        "play_count": qs.play_count or 0,
        "created_at": qs.created_at,
        "updated_at": qs.updated_at,
        "creator_name": qs.creator.name if qs.creator else None,
        "group_name": qs.group.name if qs.group else None,
        "cards": [
            {
                "id": c.id,
                "quiz_set_id": c.quiz_set_id,
                "question": c.question,
                "answer": c.answer,
                "answer_type": c.answer_type,
                "options": c.options,
                "correct_option": c.correct_option,
                "hint": c.hint,
                "order": c.order,
                "created_at": c.created_at,
            }
            for c in (qs.cards or [])
        ],
    }


def _result_to_response(r) -> dict:
    """Convert QuizResult ORM to response dict."""
    return {
        "id": r.id,
        "quiz_set_id": r.quiz_set_id,
        "user_id": r.user_id,
        "total_questions": r.total_questions,
        "correct_answers": r.correct_answers,
        "score_percentage": r.score_percentage,
        "time_spent_seconds": r.time_spent_seconds,
        "mode": r.mode,
        "completed_at": r.completed_at,
        "user_name": r.user.name if r.user else None,
    }


@router.post("/results")
async def save_quiz_result(
    data: QuizResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save quiz result after completing a quiz."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    result = await service.save_result(data, current_user.id)
    return _result_to_response(result)


@router.get("/check-access")
async def check_quiz_access(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check if user has access to quizzes (plus+ subscription)."""
    try:
        await _check_quiz_subscription(db, current_user.id, current_user.role)
        return {"has_access": True, "reason": None}
    except HTTPException as e:
        return {"has_access": False, "reason": e.detail}


@router.get("/my/results")
async def get_my_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's quiz results."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    results = await service.get_results(user_id=current_user.id, limit=50)
    return {"items": [_result_to_response(r) for r in results]}


# ============ QuizSet Endpoints ============


@router.get("")
async def list_quiz_sets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    my_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List quiz sets visible to current user.
    - Students/Leaders see their group's sets + public sets
    - If my_only=true, only show user's own sets
    """
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    
    group_id = await service.get_user_group_id(current_user.id)
    creator_id = current_user.id if my_only else None
    
    sets, total = await service.list_sets(
        page=page,
        page_size=page_size,
        group_id=group_id if not my_only else None,
        creator_id=creator_id,
        search=search,
    )
    
    return {
        "items": [_set_to_response(s) for s in sets],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_quiz_set(
    data: QuizSetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new quiz set with cards."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    group_id = await service.get_user_group_id(current_user.id)
    
    quiz_set = await service.create_set(data, current_user.id, group_id)
    return _set_to_response(quiz_set)


@router.get("/{set_id}")
async def get_quiz_set(
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get quiz set with all cards."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    quiz_set = await service.get_set_by_id(set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set topilmadi")
    return _set_to_response(quiz_set)


@router.put("/{set_id}")
async def update_quiz_set(
    set_id: int,
    data: QuizSetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a quiz set (only creator can update)."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    quiz_set = await service.get_set_by_id(set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set topilmadi")
    if quiz_set.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Faqat yaratuvchi o'zgartira oladi")
    
    updated = await service.update_set(set_id, data)
    return _set_to_response(updated)


@router.delete("/{set_id}")
async def delete_quiz_set(
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a quiz set (only creator can delete)."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    quiz_set = await service.get_set_by_id(set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set topilmadi")
    if quiz_set.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Faqat yaratuvchi o'chira oladi")
    
    await service.delete_set(set_id)
    return {"message": "Quiz set o'chirildi"}


# ============ QuizCard Endpoints ============


@router.post("/{set_id}/cards")
async def add_card(
    set_id: int,
    data: QuizCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a card to a quiz set."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    quiz_set = await service.get_set_by_id(set_id)
    if not quiz_set:
        raise HTTPException(status_code=404, detail="Quiz set topilmadi")
    if quiz_set.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Faqat yaratuvchi kartochka qo'sha oladi")
    
    card = await service.add_card(set_id, data)
    return {
        "id": card.id,
        "quiz_set_id": card.quiz_set_id,
        "question": card.question,
        "answer": card.answer,
        "answer_type": card.answer_type,
        "options": card.options,
        "correct_option": card.correct_option,
        "hint": card.hint,
        "order": card.order,
        "created_at": card.created_at,
    }


@router.put("/cards/{card_id}")
async def update_card(
    card_id: int,
    data: QuizCardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a quiz card."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    card = await service.update_card(card_id, data)
    if not card:
        raise HTTPException(status_code=404, detail="Kartochka topilmadi")
    return {
        "id": card.id,
        "quiz_set_id": card.quiz_set_id,
        "question": card.question,
        "answer": card.answer,
        "answer_type": card.answer_type,
        "options": card.options,
        "correct_option": card.correct_option,
        "hint": card.hint,
        "order": card.order,
        "created_at": card.created_at,
    }


@router.delete("/cards/{card_id}")
async def delete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a quiz card."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    result = await service.delete_card(card_id)
    if not result:
        raise HTTPException(status_code=404, detail="Kartochka topilmadi")
    return {"message": "Kartochka o'chirildi"}


# ============ Quiz Results ============


@router.get("/{set_id}/results")
async def get_set_results(
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get results/leaderboard for a quiz set."""
    await _check_quiz_subscription(db, current_user.id, current_user.role)
    service = QuizService(db)
    results = await service.get_results(quiz_set_id=set_id, limit=50)
    return {"items": [_result_to_response(r) for r in results]}
