"""
UniControl - Subscription Model
================================
Subscription/payment model for group-based subscriptions.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Integer, DateTime, Date, Boolean, Text,
    ForeignKey, Numeric, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.config import TASHKENT_TZ
from app.database import Base


class SubscriptionPlanType(str, enum.Enum):
    """Obuna rejasi turlari"""
    START = "start"
    PLUS = "plus"
    PRO = "pro"
    UNLIMITED = "unlimited"


class SubscriptionStatus(str, enum.Enum):
    """Obuna holati"""
    TRIAL = "trial"          # Sinov muddati (bepul)
    ACTIVE = "active"        # Faol obuna
    EXPIRED = "expired"      # Muddati tugagan
    BLOCKED = "blocked"      # Bloklangan (to'lov qilinmagan)
    CANCELLED = "cancelled"  # Bekor qilingan
    PAUSED = "paused"        # To'xtatilgan (pauza)


class PaymentStatus(str, enum.Enum):
    """To'lov holati"""
    PENDING = "pending"      # Kutilmoqda (chek yuborilgan)
    APPROVED = "approved"    # Tasdiqlangan
    REJECTED = "rejected"    # Rad etilgan


class SubscriptionPlan(Base):
    """Obuna rejasi"""
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # Start, Plus, Pro, Unlimited
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # narx so'mda
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)  # 30 kun
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ))


class GroupSubscription(Base):
    """Guruh obunasi"""
    __tablename__ = "group_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)  # start, plus, pro, unlimited
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SubscriptionStatus.TRIAL.value
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ), onupdate=lambda: datetime.now(TASHKENT_TZ)
    )

    # Relationships
    group = relationship("Group", backref="subscriptions")


class SubscriptionPayment(Base):
    """Obuna to'lovi"""
    __tablename__ = "subscription_payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PaymentStatus.PENDING.value
    )
    paid_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    receipt_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # chek fayl yo'li
    receipt_filename: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ))

    # Relationships
    group = relationship("Group", backref="payments")
    payer = relationship("User", foreign_keys=[paid_by_user_id])
    approver = relationship("User", foreign_keys=[approved_by])


class SubscriptionSettings(Base):
    """Obuna tizim sozlamalari (super admin)"""
    __tablename__ = "subscription_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    card_holder: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trial_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # sinov muddati tugash sanasi
    is_subscription_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ), onupdate=lambda: datetime.now(TASHKENT_TZ)
    )
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
