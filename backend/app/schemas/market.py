"""
UniControl - UniMarket Schemas
===============================
Pydantic schemas for market API request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re

from app.models.market import (
    MarketTariff, ListingStatus, ListingCategory,
    MarketOrderStatus, EscrowStatus, DisputeStatus, PayoutStatus
)


# ==================== Market Profile ====================

class MarketProfileResponse(BaseModel):
    id: int
    user_id: int
    tariff: MarketTariff
    tariff_expires_at: Optional[datetime] = None
    tariff_source: Optional[str] = None  # "group_subscription" or "individual"
    group_plan: Optional[str] = None  # pro/unlimited if from group
    balance: float
    total_earned: float
    total_spent: float
    seller_rating: float
    buyer_rating: float
    completed_orders_as_seller: int
    completed_orders_as_buyer: int
    active_orders: int
    is_verified: bool
    card_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MarketProfileUpdate(BaseModel):
    card_number: Optional[str] = None
    card_holder: Optional[str] = None


class TariffUpgradeRequest(BaseModel):
    tariff: MarketTariff


# ==================== Listings ====================

class ListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    category: ListingCategory
    subject: Optional[str] = None
    direction: Optional[str] = None
    price: float = Field(..., gt=0)
    delivery_days: int = Field(default=3, ge=1, le=30)
    max_revisions: int = Field(default=2, ge=0, le=5)
    images: Optional[List[str]] = None


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=5000)
    category: Optional[ListingCategory] = None
    subject: Optional[str] = None
    direction: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    delivery_days: Optional[int] = Field(None, ge=1, le=30)
    max_revisions: Optional[int] = Field(None, ge=0, le=5)
    images: Optional[List[str]] = None


class ListingResponse(BaseModel):
    id: int
    seller_id: int
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    title: str
    description: str
    category: ListingCategory
    subject: Optional[str] = None
    direction: Optional[str] = None
    price: float
    currency: str
    delivery_days: int
    max_revisions: int
    status: ListingStatus
    rejection_reason: Optional[str] = None
    views: int
    orders_count: int
    images: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ListingModerationAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    reason: Optional[str] = None


# ==================== Orders ====================

class OrderCreate(BaseModel):
    listing_id: int
    description: Optional[str] = None
    requirements: Optional[str] = None
    deadline_days: Optional[int] = Field(None, ge=1, le=30)


class OrderResponse(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    amount: float
    commission_rate: float
    commission_amount: float
    seller_amount: float
    deadline: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: MarketOrderStatus
    revision_count: int
    max_revisions: int
    delivery_file: Optional[str] = None
    delivery_note: Optional[str] = None
    buyer_rating: Optional[int] = None
    buyer_review: Optional[str] = None
    seller_rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Enriched fields
    listing_title: Optional[str] = None
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    escrow_status: Optional[str] = None

    class Config:
        from_attributes = True


class OrderDelivery(BaseModel):
    delivery_note: Optional[str] = None
    delivery_file: Optional[str] = None


class OrderAcceptance(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None


class OrderRevisionRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=1000)


# ==================== Escrow ====================

class EscrowResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    commission: float
    seller_payout: float
    status: EscrowStatus
    paid_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Disputes ====================

class DisputeCreate(BaseModel):
    reason: str = Field(..., min_length=20, max_length=2000)


class DisputeResponse(BaseModel):
    id: int
    order_id: int
    opened_by: int
    reason: str
    evidence: Optional[dict] = None
    status: DisputeStatus
    resolved_by: Optional[int] = None
    resolution_note: Optional[str] = None
    buyer_refund: float
    seller_payout: float
    created_at: datetime
    resolved_at: Optional[datetime] = None

    # Enriched
    opener_name: Optional[str] = None
    resolver_name: Optional[str] = None
    order_title: Optional[str] = None
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None

    class Config:
        from_attributes = True


class DisputeResolve(BaseModel):
    resolution: str = Field(..., pattern="^(buyer|seller|split)$")
    note: str = Field(..., min_length=10, max_length=2000)
    buyer_percent: Optional[float] = Field(None, ge=0, le=100)


# ==================== Chat ====================

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field(default="text", pattern="^(text|file)$")
    file_url: Optional[str] = None
    file_name: Optional[str] = None

    @validator("content")
    def block_links(cls, v):
        """Block URLs, phone numbers, Telegram links"""
        patterns = [
            r'https?://\S+',
            r'www\.\S+',
            r't\.me/\S+',
            r'@\w+',
            r'\+?\d{10,}',
        ]
        for pattern in patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(
                    "Xavfsizlik sababli havolalar, telefon raqamlari va ijtimoiy tarmoq manzillari taqiqlangan"
                )
        return v


class MessageResponse(BaseModel):
    id: int
    order_id: int
    sender_id: int
    sender_name: Optional[str] = None
    content: str
    message_type: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    is_system: bool
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Payouts ====================

class PayoutRequest(BaseModel):
    amount: float = Field(..., gt=0)
    card_number: Optional[str] = None


class PayoutResponse(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None
    amount: float
    card_number: Optional[str] = None
    status: PayoutStatus
    requested_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Dashboard Stats (admin) ====================

class MarketStats(BaseModel):
    total_listings: int = 0
    active_listings: int = 0
    pending_listings: int = 0
    total_orders: int = 0
    active_orders: int = 0
    completed_orders: int = 0
    disputed_orders: int = 0
    total_escrow_held: float = 0.0
    total_commission_earned: float = 0.0
    total_payouts: float = 0.0
    total_users: int = 0
    pro_users: int = 0
    premium_users: int = 0
