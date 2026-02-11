"""
UniControl - Subscription API Routes
=====================================
Subscription management for groups.

Author: UniControl Team
Version: 1.0.0
"""

import os
import uuid
import json
from datetime import datetime, date, timedelta
from app.config import now_tashkent, today_tashkent
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from pydantic import BaseModel

from app.database import get_db
from app.models.subscription import (
    SubscriptionPlan, GroupSubscription, SubscriptionPayment,
    SubscriptionSettings, SubscriptionStatus, PaymentStatus,
    SubscriptionPlanType,
)
from app.models.group import Group
from app.models.student import Student
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.core.dependencies import get_current_active_user, require_admin, require_superadmin

router = APIRouter()


# ===== Pydantic schemas =====

class PlanResponse(BaseModel):
    id: int
    name: str
    plan_type: str
    price: int
    duration_days: int
    description: Optional[str] = None
    features: Optional[List[str]] = None
    is_active: bool

class PlanCreate(BaseModel):
    name: str
    plan_type: str
    price: int
    duration_days: int = 30
    description: Optional[str] = None
    features: Optional[List[str]] = None

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class SubscriptionResponse(BaseModel):
    id: int
    group_id: int
    group_name: Optional[str] = None
    plan_type: str
    status: str
    start_date: str
    end_date: str
    is_trial: bool
    days_left: int = 0
    created_at: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    group_id: int
    group_name: Optional[str] = None
    plan_type: str
    amount: int
    status: str
    paid_by_user_id: Optional[int] = None
    paid_by_name: Optional[str] = None
    receipt_file: Optional[str] = None
    receipt_filename: Optional[str] = None
    admin_note: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    created_at: Optional[str] = None

class SettingsResponse(BaseModel):
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    trial_end_date: Optional[str] = None
    is_subscription_enabled: bool = True

class SettingsUpdate(BaseModel):
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    trial_end_date: Optional[str] = None
    is_subscription_enabled: Optional[bool] = None

class PaymentAction(BaseModel):
    status: str  # approved or rejected
    admin_note: Optional[str] = None


# ===== Helper functions =====

def _plan_to_response(plan: SubscriptionPlan) -> dict:
    features = []
    if plan.features:
        try:
            features = json.loads(plan.features)
        except:
            features = []
    return {
        "id": plan.id,
        "name": plan.name,
        "plan_type": plan.plan_type,
        "price": plan.price,
        "duration_days": plan.duration_days,
        "description": plan.description,
        "features": features,
        "is_active": plan.is_active,
    }


async def _get_or_create_settings(db: AsyncSession) -> SubscriptionSettings:
    result = await db.execute(select(SubscriptionSettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SubscriptionSettings(
            card_number="8600 0000 0000 0000",
            card_holder="UNICONTROL",
            trial_end_date=date(2026, 2, 28),
            is_subscription_enabled=True,
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


async def _get_group_subscription(db: AsyncSession, group_id: int) -> Optional[GroupSubscription]:
    """Guruhning faol obunasini olish"""
    result = await db.execute(
        select(GroupSubscription)
        .where(
            GroupSubscription.group_id == group_id,
            GroupSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ])
        )
        .order_by(GroupSubscription.end_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ===== Plans =====

@router.get("/plans")
async def get_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Barcha obuna rejalarini olish"""
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.sort_order)
    )
    plans = result.scalars().all()

    # Agar rejalar bo'lmasa, default yaratish
    if not plans:
        defaults = [
            SubscriptionPlan(name="Start", plan_type="start", price=30000,
                             duration_days=30, description="Boshlang'ich reja",
                             features=json.dumps(["Davomat", "Jadval", "Hisobotlar"]),
                             sort_order=1),
            SubscriptionPlan(name="Plus", plan_type="plus", price=40000,
                             duration_days=30, description="Kengaytirilgan reja",
                             features=json.dumps(["Davomat", "Jadval", "Hisobotlar", "Kutubxona", "To'garaklar", "Telegram Bot"]),
                             sort_order=2),
            SubscriptionPlan(name="Pro", plan_type="pro", price=50000,
                             duration_days=30, description="Professional reja",
                             features=json.dumps(["Davomat", "Jadval", "Hisobotlar", "Kutubxona", "To'garaklar", "Turnirlar", "AI Tahlil", "Telegram Bot"]),
                             sort_order=3),
            SubscriptionPlan(name="Unlimited", plan_type="unlimited", price=55000,
                             duration_days=30, description="Cheksiz reja",
                             features=json.dumps(["Barcha funksiyalar", "Davomat", "Jadval", "Hisobotlar", "Kutubxona", "To'garaklar", "Turnirlar", "AI Tahlil", "Oshxona", "Fayllar", "Telegram Bot"]),
                             sort_order=4),
        ]
        for p in defaults:
            db.add(p)
        await db.commit()

        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.sort_order)
        )
        plans = result.scalars().all()

    return [_plan_to_response(p) for p in plans]


@router.post("/plans")
async def create_plan(
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Yangi obuna rejasi yaratish (super admin)"""
    plan = SubscriptionPlan(
        name=data.name,
        plan_type=data.plan_type,
        price=data.price,
        duration_days=data.duration_days,
        description=data.description,
        features=json.dumps(data.features) if data.features else None,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return _plan_to_response(plan)


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obuna rejasini tahrirlash (super admin)"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    if data.name is not None:
        plan.name = data.name
    if data.price is not None:
        plan.price = data.price
    if data.duration_days is not None:
        plan.duration_days = data.duration_days
    if data.description is not None:
        plan.description = data.description
    if data.features is not None:
        plan.features = json.dumps(data.features)
    if data.is_active is not None:
        plan.is_active = data.is_active
    if data.sort_order is not None:
        plan.sort_order = data.sort_order

    await db.commit()
    await db.refresh(plan)
    return _plan_to_response(plan)


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obuna rejasini o'chirish (super admin)"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    # Soft delete — deactivate instead of hard delete
    plan.is_active = False
    await db.commit()
    return {"message": f"'{plan.name}' rejasi o'chirildi", "id": plan.id}


# ===== Group subscription status =====

@router.get("/my-group")
async def get_my_group_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Joriy foydalanuvchining guruh obunasini olish"""
    # Find student / group
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()

    # Leader managed group
    group_id = None
    group_name = None
    if student and student.group_id:
        group_id = student.group_id
        grp = await db.execute(select(Group).where(Group.id == group_id))
        g = grp.scalar_one_or_none()
        group_name = g.name if g else None
    
    if not group_id:
        return {"subscription": None, "is_blocked": False, "group_id": None}

    # Check trial
    settings = await _get_or_create_settings(db)
    today = today_tashkent()

    sub = await _get_group_subscription(db, group_id)

    if sub:
        days_left = max(0, (sub.end_date - today).days)
        is_blocked = sub.status in (SubscriptionStatus.EXPIRED.value, SubscriptionStatus.BLOCKED.value)
        if today > sub.end_date and sub.status in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value):
            sub.status = SubscriptionStatus.EXPIRED.value
            await db.commit()
            is_blocked = True
            days_left = 0

        return {
            "subscription": {
                "id": sub.id,
                "group_id": sub.group_id,
                "group_name": group_name,
                "plan_type": sub.plan_type,
                "status": sub.status,
                "start_date": sub.start_date.isoformat(),
                "end_date": sub.end_date.isoformat(),
                "is_trial": sub.is_trial,
                "days_left": days_left,
            },
            "is_blocked": is_blocked,
            "group_id": group_id,
            "group_name": group_name,
        }
    else:
        # Check if in trial period
        if settings.trial_end_date and today <= settings.trial_end_date:
            return {
                "subscription": {
                    "id": 0,
                    "group_id": group_id,
                    "group_name": group_name,
                    "plan_type": "trial",
                    "status": "trial",
                    "start_date": today.isoformat(),
                    "end_date": settings.trial_end_date.isoformat(),
                    "is_trial": True,
                    "days_left": (settings.trial_end_date - today).days,
                },
                "is_blocked": False,
                "group_id": group_id,
                "group_name": group_name,
            }
        else:
            return {
                "subscription": None,
                "is_blocked": True,
                "group_id": group_id,
                "group_name": group_name,
            }


@router.get("/check/{group_id}")
async def check_group_subscription(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Guruh obunasini tekshirish"""
    settings = await _get_or_create_settings(db)
    today = today_tashkent()

    sub = await _get_group_subscription(db, group_id)
    grp_result = await db.execute(select(Group).where(Group.id == group_id))
    grp = grp_result.scalar_one_or_none()

    if sub:
        if today > sub.end_date:
            sub.status = SubscriptionStatus.EXPIRED.value
            await db.commit()
        days_left = max(0, (sub.end_date - today).days)
        return {
            "is_active": sub.status in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value) and today <= sub.end_date,
            "plan_type": sub.plan_type,
            "status": sub.status,
            "end_date": sub.end_date.isoformat(),
            "days_left": days_left,
        }
    elif settings.trial_end_date and today <= settings.trial_end_date:
        return {
            "is_active": True,
            "plan_type": "trial",
            "status": "trial",
            "end_date": settings.trial_end_date.isoformat(),
            "days_left": (settings.trial_end_date - today).days,
        }
    else:
        return {
            "is_active": False,
            "plan_type": None,
            "status": "blocked",
            "end_date": None,
            "days_left": 0,
        }


# ===== Payment / Purchase =====

@router.post("/purchase")
async def purchase_subscription(
    group_id: int = Form(...),
    plan_type: str = Form(...),
    receipt: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obunani sotib olish (chek yuborish)"""
    # Get plan
    plan_result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.plan_type == plan_type,
            SubscriptionPlan.is_active == True
        )
    )
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    # Check group exists
    grp_result = await db.execute(select(Group).where(Group.id == group_id))
    grp = grp_result.scalar_one_or_none()
    if not grp:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    # Save receipt file
    upload_dir = f"uploads/receipts/{group_id}"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(receipt.filename)[1].lower() if receipt.filename else ".jpg"
    allowed_exts = {".jpg", ".jpeg", ".png", ".pdf", ".webp"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Ruxsat etilgan formatlar: {', '.join(allowed_exts)}")
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await receipt.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Create payment record
    payment = SubscriptionPayment(
        group_id=group_id,
        plan_type=plan_type,
        amount=plan.price,
        status=PaymentStatus.PENDING.value,
        paid_by_user_id=current_user.id,
        receipt_file=filepath,
        receipt_filename=receipt.filename,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    # Notify super admins
    try:
        admin_result = await db.execute(
            select(User.id).where(User.role.in_(["superadmin", "admin"]), User.is_active == True)
        )
        admin_ids = [r[0] for r in admin_result.all()]
        for aid in admin_ids:
            notif = Notification(
                user_id=aid,
                title="Yangi to'lov cheki keldi 💰",
                message=f"\"{grp.name}\" guruhi uchun {plan.name} ({plan.price:,} so'm) obuna to'lovi cheki yuborildi. Tekshiring!",
                type=NotificationType.INFO,
                priority=NotificationPriority.HIGH,
            )
            db.add(notif)
        await db.commit()
    except Exception as e:
        logger.warning(f"Payment notification error: {e}")

    return {
        "id": payment.id,
        "status": payment.status,
        "message": "To'lov cheki yuborildi. Admin tasdiqlashini kuting."
    }


@router.get("/payments")
async def list_payments(
    status_filter: Optional[str] = Query(None, alias="status"),
    group_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'lovlar ro'yxati (admin/super)"""
    query = select(SubscriptionPayment)
    count_query = select(func.count(SubscriptionPayment.id))

    if status_filter:
        query = query.where(SubscriptionPayment.status == status_filter)
        count_query = count_query.where(SubscriptionPayment.status == status_filter)
    if group_id:
        query = query.where(SubscriptionPayment.group_id == group_id)
        count_query = count_query.where(SubscriptionPayment.group_id == group_id)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(SubscriptionPayment.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    payments = result.scalars().all()

    items = []
    for p in payments:
        # Get group name
        grp_result = await db.execute(select(Group.name).where(Group.id == p.group_id))
        grp_name = grp_result.scalar() or "?"

        # Get payer name
        payer_name = None
        if p.paid_by_user_id:
            user_result = await db.execute(select(User.name).where(User.id == p.paid_by_user_id))
            payer_name = user_result.scalar()

        items.append({
            "id": p.id,
            "group_id": p.group_id,
            "group_name": grp_name,
            "plan_type": p.plan_type,
            "amount": p.amount,
            "status": p.status,
            "paid_by_user_id": p.paid_by_user_id,
            "paid_by_name": payer_name,
            "receipt_file": p.receipt_file,
            "receipt_filename": p.receipt_filename,
            "admin_note": p.admin_note,
            "approved_by": p.approved_by,
            "approved_at": p.approved_at.isoformat() if p.approved_at else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.patch("/payments/{payment_id}")
async def action_payment(
    payment_id: int,
    data: PaymentAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """To'lovni tasdiqlash/rad etish (super admin)"""
    result = await db.execute(
        select(SubscriptionPayment).where(SubscriptionPayment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")

    payment.status = data.status
    payment.admin_note = data.admin_note
    payment.approved_by = current_user.id
    payment.approved_at = now_tashkent()

    if data.status == PaymentStatus.APPROVED.value:
        # Get plan
        plan_result = await db.execute(
            select(SubscriptionPlan).where(
                SubscriptionPlan.plan_type == payment.plan_type,
                SubscriptionPlan.is_active == True
            )
        )
        plan = plan_result.scalar_one_or_none()
        duration = plan.duration_days if plan else 30

        # Activate subscription for group
        today = today_tashkent()

        # Check existing active subscription
        existing = await _get_group_subscription(db, payment.group_id)
        if existing and existing.end_date >= today:
            # Extend existing
            existing.end_date = existing.end_date + timedelta(days=duration)
            existing.plan_type = payment.plan_type
            existing.status = SubscriptionStatus.ACTIVE.value
        else:
            # Create new subscription
            new_sub = GroupSubscription(
                group_id=payment.group_id,
                plan_type=payment.plan_type,
                status=SubscriptionStatus.ACTIVE.value,
                start_date=today,
                end_date=today + timedelta(days=duration),
                is_trial=False,
            )
            db.add(new_sub)

        # Notify group members
        try:
            grp_result = await db.execute(select(Group.name).where(Group.id == payment.group_id))
            grp_name = grp_result.scalar() or "Guruh"

            students_result = await db.execute(
                select(Student.user_id)
                .where(Student.group_id == payment.group_id, Student.user_id.isnot(None))
            )
            user_ids = [r[0] for r in students_result.all()]

            plan_name = plan.name if plan else payment.plan_type
            for uid in user_ids:
                notif = Notification(
                    user_id=uid,
                    title="Obuna faollashtirildi ✅",
                    message=f"\"{grp_name}\" guruhi uchun \"{plan_name}\" obunasi {duration} kunga faollashtirildi!",
                    type=NotificationType.SUCCESS,
                    priority=NotificationPriority.HIGH,
                    sender_id=current_user.id,
                )
                db.add(notif)
        except Exception as e:
            logger.warning(f"Subscription activation notification error: {e}")

    elif data.status == PaymentStatus.REJECTED.value:
        # Notify payer
        try:
            if payment.paid_by_user_id:
                grp_result = await db.execute(select(Group.name).where(Group.id == payment.group_id))
                grp_name = grp_result.scalar() or "Guruh"
                notif = Notification(
                    user_id=payment.paid_by_user_id,
                    title="To'lov rad etildi ❌",
                    message=f"\"{grp_name}\" guruhi uchun yuborgan to'lov chekingiz rad etildi. Sabab: {data.admin_note or 'ko`rsatilmagan'}",
                    type=NotificationType.WARNING,
                    priority=NotificationPriority.HIGH,
                    sender_id=current_user.id,
                )
                db.add(notif)
        except Exception as e:
            logger.warning(f"Payment rejection notification error: {e}")

    await db.commit()

    return {"id": payment.id, "status": payment.status, "message": "To'lov yangilandi"}


# ===== Settings (super admin) =====

@router.get("/settings")
async def get_subscription_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obuna sozlamalarini olish"""
    settings = await _get_or_create_settings(db)
    return {
        "card_number": settings.card_number,
        "card_holder": settings.card_holder,
        "trial_end_date": settings.trial_end_date.isoformat() if settings.trial_end_date else None,
        "is_subscription_enabled": settings.is_subscription_enabled,
    }


@router.put("/settings")
async def update_subscription_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obuna sozlamalarini yangilash (super admin)"""
    settings = await _get_or_create_settings(db)

    if data.card_number is not None:
        settings.card_number = data.card_number
    if data.card_holder is not None:
        settings.card_holder = data.card_holder
    if data.trial_end_date is not None:
        settings.trial_end_date = date.fromisoformat(data.trial_end_date)
    if data.is_subscription_enabled is not None:
        settings.is_subscription_enabled = data.is_subscription_enabled
    settings.updated_by = current_user.id

    await db.commit()
    await db.refresh(settings)
    return {
        "card_number": settings.card_number,
        "card_holder": settings.card_holder,
        "trial_end_date": settings.trial_end_date.isoformat() if settings.trial_end_date else None,
        "is_subscription_enabled": settings.is_subscription_enabled,
    }


# ===== Activate trial for all groups (super admin START button) =====

@router.post("/activate-trial")
async def activate_trial(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Barcha guruhlar uchun bepul sinov muddatini faollashtirish"""
    settings = await _get_or_create_settings(db)
    trial_end = date(2026, 2, 28)
    settings.trial_end_date = trial_end
    await db.commit()

    # Notify all users
    try:
        all_users = await db.execute(
            select(User.id).where(User.is_active == True)
        )
        user_ids = [r[0] for r in all_users.all()]
        for uid in user_ids:
            notif = Notification(
                user_id=uid,
                title="Bepul sinov muddati boshlandi! 🎉",
                message=f"UniControl platformasi 28-fevral 2026 kechki 23:59 gacha barcha guruhlar uchun bepul! Undan keyin obuna talab qilinadi.",
                type=NotificationType.ANNOUNCEMENT,
                priority=NotificationPriority.HIGH,
                sender_id=current_user.id,
            )
            db.add(notif)
        await db.commit()
    except Exception as e:
        logger.warning(f"Trial activation notification error: {e}")

    return {
        "message": f"Bepul sinov muddati 28-fevral 2026 gacha faollashtirildi. {len(user_ids)} foydalanuvchiga xabar yuborildi.",
        "trial_end_date": trial_end.isoformat(),
    }


# ===== All subscriptions list (super admin) =====

@router.get("/all")
async def list_all_subscriptions(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Barcha guruh obunalarini olish"""
    query = select(GroupSubscription)
    count_query = select(func.count(GroupSubscription.id))

    if status_filter:
        query = query.where(GroupSubscription.status == status_filter)
        count_query = count_query.where(GroupSubscription.status == status_filter)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(GroupSubscription.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    subs = result.scalars().all()

    today = today_tashkent()
    items = []
    for s in subs:
        grp_result = await db.execute(select(Group.name).where(Group.id == s.group_id))
        grp_name = grp_result.scalar() or "?"
        days_left = max(0, (s.end_date - today).days)
        items.append({
            "id": s.id,
            "group_id": s.group_id,
            "group_name": grp_name,
            "plan_type": s.plan_type,
            "status": s.status,
            "start_date": s.start_date.isoformat(),
            "end_date": s.end_date.isoformat(),
            "is_trial": s.is_trial,
            "days_left": days_left,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ===== Update subscription status (super admin) =====

class AdminAssignSubscription(BaseModel):
    group_id: int
    plan_id: int


@router.post("/admin-assign")
async def admin_assign_subscription(
    data: AdminAssignSubscription,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Super admin tomonidan guruhga obuna berish (to'g'ridan-to'g'ri)"""
    # Get plan
    plan_result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == data.plan_id,
            SubscriptionPlan.is_active == True
        )
    )
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    # Check group exists
    grp_result = await db.execute(select(Group).where(Group.id == data.group_id))
    grp = grp_result.scalar_one_or_none()
    if not grp:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    today = today_tashkent()
    duration = plan.duration_days or 30

    # Check existing active subscription
    existing = await _get_group_subscription(db, data.group_id)
    if existing and existing.end_date >= today and existing.status in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value):
        # Extend existing
        existing.end_date = existing.end_date + timedelta(days=duration)
        existing.plan_type = plan.plan_type
        existing.status = SubscriptionStatus.ACTIVE.value
        existing.is_trial = False
        sub_id = existing.id
    else:
        # Create new subscription
        new_sub = GroupSubscription(
            group_id=data.group_id,
            plan_type=plan.plan_type,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=today,
            end_date=today + timedelta(days=duration),
            is_trial=False,
        )
        db.add(new_sub)
        await db.flush()
        sub_id = new_sub.id

    # Create payment record (admin-assigned, auto-approved)
    payment = SubscriptionPayment(
        group_id=data.group_id,
        plan_type=plan.plan_type,
        amount=plan.price,
        status=PaymentStatus.APPROVED.value,
        paid_by_user_id=current_user.id,
        admin_note=f"Super admin tomonidan tayinlandi",
        approved_by=current_user.id,
        approved_at=now_tashkent(),
    )
    db.add(payment)

    # Notify group members
    try:
        students_result = await db.execute(
            select(Student.user_id)
            .where(Student.group_id == data.group_id, Student.user_id.isnot(None))
        )
        user_ids = [r[0] for r in students_result.all()]

        for uid in user_ids:
            notif = Notification(
                user_id=uid,
                title="Obuna faollashtirildi ✅",
                message=f"\"{grp.name}\" guruhi uchun \"{plan.name}\" obunasi {duration} kunga faollashtirildi! Admin tomonidan tayinlandi.",
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.HIGH,
                sender_id=current_user.id,
            )
            db.add(notif)
    except Exception as e:
        logger.warning(f"Admin assign notification error: {e}")

    await db.commit()

    return {
        "success": True,
        "message": f"\"{grp.name}\" guruhiga \"{plan.name}\" obunasi {duration} kunga faollashtirildi",
        "subscription_id": sub_id,
        "group_name": grp.name,
        "plan_name": plan.name,
        "duration_days": duration,
        "end_date": (today + timedelta(days=duration)).isoformat(),
    }


class SubscriptionStatusUpdate(BaseModel):
    status: str  # active, paused, cancelled, blocked
    reason: Optional[str] = None


@router.patch("/subscriptions/{sub_id}/status")
async def update_subscription_status(
    sub_id: int,
    data: SubscriptionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obuna holatini o'zgartirish (bekor qilish / to'xtatish / faollashtirish)"""
    allowed = ["active", "paused", "cancelled", "blocked"]
    if data.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Noto'g'ri status. Ruxsat etilgan: {', '.join(allowed)}")

    result = await db.execute(
        select(GroupSubscription).where(GroupSubscription.id == sub_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Obuna topilmadi")

    old_status = sub.status
    sub.status = data.status
    sub.updated_at = now_tashkent()
    await db.flush()

    # Get group name for notification
    grp_result = await db.execute(select(Group.name).where(Group.id == sub.group_id))
    group_name = grp_result.scalar() or "?"

    # Status labels for notifications
    status_labels = {
        "active": "faollashtirildi ✅",
        "paused": "to'xtatildi (pauza) ⏸️",
        "cancelled": "bekor qilindi ❌",
        "blocked": "bloklandi 🚫",
    }
    status_msg = status_labels.get(data.status, data.status)

    # Send notifications to group members
    try:
        students_q = await db.execute(
            select(Student.user_id).where(Student.group_id == sub.group_id)
        )
        user_ids = [uid for (uid,) in students_q.all() if uid]

        for uid in user_ids:
            message = f"Guruhingiz \"{group_name}\" obunasi {status_msg}."
            if data.reason:
                message += f" Sabab: {data.reason}"
            notif = Notification(
                user_id=uid,
                title="Obuna holati o'zgardi",
                message=message,
                type=NotificationType.ANNOUNCEMENT,
                priority=NotificationPriority.HIGH,
                sender_id=current_user.id,
            )
            db.add(notif)
        await db.commit()
    except Exception as e:
        logger.warning(f"Subscription status notification error: {e}")
        await db.commit()

    return {
        "message": f"Obuna holati '{old_status}' dan '{data.status}' ga o'zgartirildi",
        "id": sub.id,
        "status": sub.status,
        "group_name": group_name,
    }


# ===== Serve receipt file =====

@router.get("/receipt/{payment_id}")
async def get_receipt(
    payment_id: int,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """To'lov chekini olish"""
    from fastapi.responses import FileResponse
    result = await db.execute(
        select(SubscriptionPayment).where(SubscriptionPayment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment or not payment.receipt_file:
        raise HTTPException(status_code=404, detail="Chek topilmadi")

    if not os.path.exists(payment.receipt_file):
        raise HTTPException(status_code=404, detail="Fayl topilmadi")

    # Determine media type from filename
    fname = (payment.receipt_filename or "").lower()
    if fname.endswith(".png"):
        media_type = "image/png"
    elif fname.endswith(".jpg") or fname.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif fname.endswith(".pdf"):
        media_type = "application/pdf"
    elif fname.endswith(".webp"):
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    return FileResponse(
        payment.receipt_file,
        filename=payment.receipt_filename or "receipt",
        media_type=media_type
    )