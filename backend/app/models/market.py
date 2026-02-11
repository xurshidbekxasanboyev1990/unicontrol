"""
UniControl - UniMarket Models
==============================
Models for the UniMarket marketplace system.
Includes: tariffs, listings, orders, escrow, chat, disputes.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, DateTime, Integer, BigInteger, Float,
    Text, ForeignKey, Enum as SQLEnum, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON
import enum

from app.config import TASHKENT_TZ
from app.database import Base


# ==================== Enums ====================

class MarketTariff(str, enum.Enum):
    """User tariff level for UniMarket"""
    FREE = "free"
    STUDENT_PRO = "student_pro"
    PREMIUM = "premium"


class ListingStatus(str, enum.Enum):
    """Status of a service listing"""
    DRAFT = "draft"
    PENDING = "pending"       # Awaiting moderation
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class MarketOrderStatus(str, enum.Enum):
    """Status of a market order"""
    PENDING = "pending"           # Buyer placed, awaiting seller accept
    ACCEPTED = "accepted"         # Seller accepted
    PAID = "paid"                 # Payment received, escrow hold
    IN_PROGRESS = "in_progress"   # Work started
    DELIVERED = "delivered"       # Seller delivered work
    REVISION = "revision"         # Buyer requested revision
    COMPLETED = "completed"       # Buyer accepted, payout initiated
    DISPUTED = "disputed"         # Dispute opened
    CANCELLED = "cancelled"       # Order cancelled
    REFUNDED = "refunded"         # Full refund issued


class EscrowStatus(str, enum.Enum):
    """Status of escrow (garant) funds"""
    ON_HOLD = "on_hold"
    RELEASED = "released"
    REFUNDED = "refunded"
    PARTIAL_RELEASE = "partial_release"


class DisputeStatus(str, enum.Enum):
    """Status of a dispute"""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED_BUYER = "resolved_buyer"      # In favor of buyer
    RESOLVED_SELLER = "resolved_seller"    # In favor of seller
    RESOLVED_SPLIT = "resolved_split"      # Split resolution
    CLOSED = "closed"


class PayoutStatus(str, enum.Enum):
    """Status of payout to seller"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ListingCategory(str, enum.Enum):
    """Categories for service listings"""
    PROGRAMMING = "programming"
    DESIGN = "design"
    WRITING = "writing"
    TRANSLATION = "translation"
    MATH = "math"
    SCIENCE = "science"
    TUTORING = "tutoring"
    COURSEWORK = "coursework"
    PRESENTATION = "presentation"
    RESEARCH = "research"
    OTHER = "other"


# ==================== Models ====================

class UserMarketProfile(Base):
    """
    Market profile for each user — tariff, balance, stats.
    """
    __tablename__ = "market_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    tariff: Mapped[str] = mapped_column(
        SQLEnum(MarketTariff), default=MarketTariff.FREE, nullable=False
    )
    tariff_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Balance
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Stats
    seller_rating: Mapped[float] = mapped_column(Float, default=0.0)
    buyer_rating: Mapped[float] = mapped_column(Float, default=0.0)
    completed_orders_as_seller: Mapped[int] = mapped_column(Integer, default=0)
    completed_orders_as_buyer: Mapped[int] = mapped_column(Integer, default=0)
    active_orders: Mapped[int] = mapped_column(Integer, default=0)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    card_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    card_holder: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(TASHKENT_TZ), onupdate=lambda: datetime.now(TASHKENT_TZ)
    )

    # Relationships
    user = relationship("User", backref="market_profile")
    listings = relationship("ServiceListing", back_populates="seller_profile", lazy="dynamic")


class ServiceListing(Base):
    """
    A service listing (e'lon) posted by a seller.
    """
    __tablename__ = "market_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    seller_profile_id: Mapped[int] = mapped_column(
        ForeignKey("market_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    # Listing details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        SQLEnum(ListingCategory), nullable=False, index=True
    )
    subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="UZS")

    # Delivery
    delivery_days: Mapped[int] = mapped_column(Integer, default=3)
    max_revisions: Mapped[int] = mapped_column(Integer, default=2)

    # Status & moderation
    status: Mapped[str] = mapped_column(
        SQLEnum(ListingStatus), default=ListingStatus.PENDING, nullable=False, index=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    moderated_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    moderated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Stats
    views: Mapped[int] = mapped_column(Integer, default=0)
    orders_count: Mapped[int] = mapped_column(Integer, default=0)

    # Images / attachments stored as JSON list of paths
    images: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(TASHKENT_TZ), onupdate=lambda: datetime.now(TASHKENT_TZ)
    )

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], backref="market_listings")
    seller_profile = relationship("UserMarketProfile", back_populates="listings")
    orders = relationship("MarketOrder", back_populates="listing", lazy="dynamic")


class MarketOrder(Base):
    """
    An order placed by a buyer for a service listing.
    Includes escrow (garant) mechanism.
    """
    __tablename__ = "market_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Parties
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("market_listings.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Order details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Financial
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.10)  # 10%
    commission_amount: Mapped[float] = mapped_column(Float, default=0.0)
    seller_amount: Mapped[float] = mapped_column(Float, default=0.0)

    # Timeline
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(
            MarketOrderStatus,
            name="marketorderstatus",
            values_callable=lambda x: [e.value for e in x]
        ),
        default=MarketOrderStatus.PENDING, nullable=False, index=True
    )
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    max_revisions: Mapped[int] = mapped_column(Integer, default=2)

    # Payment receipt (buyer uploads proof of payment)
    payment_receipt: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    payment_receipt_filename: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Delivery file
    delivery_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    delivery_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Rating (after completion)
    buyer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    buyer_review: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seller_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(TASHKENT_TZ), onupdate=lambda: datetime.now(TASHKENT_TZ)
    )

    # Relationships
    listing = relationship("ServiceListing", back_populates="orders")
    buyer = relationship("User", foreign_keys=[buyer_id], backref="market_orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], backref="market_orders_as_seller")
    escrow = relationship("EscrowTransaction", back_populates="order", uselist=False)
    dispute = relationship("MarketDispute", back_populates="order", uselist=False)
    messages = relationship("MarketMessage", back_populates="order", lazy="dynamic")


class EscrowTransaction(Base):
    """
    Garant (escrow) — UniControl holds the money until work is accepted.
    """
    __tablename__ = "market_escrow"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("market_orders.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    commission: Mapped[float] = mapped_column(Float, default=0.0)
    seller_payout: Mapped[float] = mapped_column(Float, default=0.0)

    status: Mapped[str] = mapped_column(
        SQLEnum(EscrowStatus), default=EscrowStatus.ON_HOLD, nullable=False
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))

    # Relationships
    order = relationship("MarketOrder", back_populates="escrow")


class MarketDispute(Base):
    """
    Dispute opened when buyer/seller disagree.
    Resolved by admin/superadmin.
    """
    __tablename__ = "market_disputes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("market_orders.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    opened_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # file paths

    status: Mapped[str] = mapped_column(
        SQLEnum(DisputeStatus), default=DisputeStatus.OPEN, nullable=False
    )

    # Resolution
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    buyer_refund: Mapped[float] = mapped_column(Float, default=0.0)
    seller_payout: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    order = relationship("MarketOrder", back_populates="dispute")
    opener = relationship("User", foreign_keys=[opened_by])
    resolver = relationship("User", foreign_keys=[resolved_by])


class MarketMessage(Base):
    """
    Chat messages within an order — buyer ↔ seller (+ admin can view).
    Links are auto-blocked.
    """
    __tablename__ = "market_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("market_orders.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(20), default="text"  # text, file, system
    )
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))

    # Relationships
    order = relationship("MarketOrder", back_populates="messages")
    sender = relationship("User", backref="market_messages_sent")


class SellerPayout(Base):
    """
    Track payouts from platform balance to seller's card.
    """
    __tablename__ = "market_payouts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("market_orders.id"), nullable=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    card_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(PayoutStatus), default=PayoutStatus.PENDING, nullable=False
    )

    requested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="market_payouts")


class MarketTariffPayment(Base):
    """
    Tariff payment record — user uploads receipt to upgrade market tariff.
    Approved by super admin.
    """
    __tablename__ = "market_tariff_payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tariff: Mapped[str] = mapped_column(
        SQLEnum(MarketTariff), nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, approved, rejected
    receipt_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    receipt_filename: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(TASHKENT_TZ))

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="market_tariff_payments")
    approver = relationship("User", foreign_keys=[approved_by])


# ==================== Tariff Limits Config ====================

TARIFF_LIMITS = {
    MarketTariff.FREE: {
        "can_create_listing": False,
        "can_order": True,
        "can_chat": False,
        "can_escrow": False,
        "max_active_orders": 0,
        "max_amount_per_order": 0,
        "monthly_limit": 0,
        "commission_rate": 0.15,
        "payout_delay_hours": 72,
    },
    MarketTariff.STUDENT_PRO: {
        "can_create_listing": True,
        "can_order": True,
        "can_chat": True,
        "can_escrow": True,
        "max_active_orders": 3,
        "max_amount_per_order": 2_000_000,  # 2 mln UZS
        "monthly_limit": 5_000_000,
        "commission_rate": 0.10,
        "payout_delay_hours": 48,
    },
    MarketTariff.PREMIUM: {
        "can_create_listing": True,
        "can_order": True,
        "can_chat": True,
        "can_escrow": True,
        "max_active_orders": 10,
        "max_amount_per_order": 10_000_000,  # 10 mln UZS
        "monthly_limit": 50_000_000,
        "commission_rate": 0.07,
        "payout_delay_hours": 24,
    },
}
