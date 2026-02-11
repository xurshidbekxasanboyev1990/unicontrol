"""
UniControl - UniMarket API Routes
====================================
REST + WebSocket endpoints for marketplace.
"""

from datetime import datetime, timedelta
from app.config import now_tashkent
from typing import Optional
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
import json
import os
import uuid

from app.database import get_db
from app.models.user import User, UserRole
from app.models.market import (
    UserMarketProfile, ServiceListing, MarketOrder,
    MarketMessage, MarketDispute, SellerPayout,
    MarketTariffPayment, MarketTariff,
    ListingStatus, MarketOrderStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.subscription import SubscriptionSettings
from app.schemas.market import (
    ListingCreate, ListingUpdate, ListingResponse, ListingModerationAction,
    OrderCreate, OrderResponse, OrderDelivery, OrderAcceptance, OrderRevisionRequest,
    MarketProfileResponse, MarketProfileUpdate, TariffUpgradeRequest,
    MessageCreate, MessageResponse,
    DisputeCreate, DisputeResponse, DisputeResolve,
    PayoutRequest, PayoutResponse,
    EscrowResponse, MarketStats
)
from app.services.market_service import MarketService
from app.core.dependencies import (
    get_current_active_user, require_admin, require_superadmin
)
from app.core.security import verify_token

router = APIRouter()


# ==================== WebSocket Connection Manager ====================

class ConnectionManager:
    """Manages WebSocket connections for real-time market chat"""

    def __init__(self):
        # {order_id: {user_id: WebSocket}}
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, order_id: int, user_id: int):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = {}
        self.active_connections[order_id][user_id] = websocket
        logger.info(f"WS connected: user={user_id}, order={order_id}")

    def disconnect(self, order_id: int, user_id: int):
        if order_id in self.active_connections:
            self.active_connections[order_id].pop(user_id, None)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]
        logger.info(f"WS disconnected: user={user_id}, order={order_id}")

    async def send_to_order(self, order_id: int, message: dict, exclude_user: int = None):
        """Broadcast message to all connected users of an order"""
        if order_id in self.active_connections:
            for user_id, ws in self.active_connections[order_id].items():
                if user_id != exclude_user:
                    try:
                        await ws.send_json(message)
                    except Exception as e:
                        logger.warning(f"WebSocket send failed for user {user_id}: {e}")


manager = ConnectionManager()


# ==================== Profile ====================

@router.get("/market/profile", response_model=MarketProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get or create current user's market profile"""
    profile = await MarketService.get_or_create_profile(db, current_user.id)
    await db.commit()

    # Build response with tariff_source info
    resp = MarketProfileResponse.model_validate(profile)
    resp.tariff_source = getattr(profile, '_tariff_source', 'individual')
    resp.group_plan = getattr(profile, '_group_plan', None)
    return resp


@router.put("/market/profile", response_model=MarketProfileResponse)
async def update_my_profile(
    data: MarketProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update market profile (card info)"""
    profile = await MarketService.update_profile(
        db, current_user.id,
        card_number=data.card_number,
        card_holder=data.card_holder
    )
    await db.commit()

    # Re-fetch with group subscription check to get tariff_source
    profile = await MarketService.get_or_create_profile(db, current_user.id)
    resp = MarketProfileResponse.model_validate(profile)
    resp.tariff_source = getattr(profile, '_tariff_source', 'individual')
    resp.group_plan = getattr(profile, '_group_plan', None)
    return resp


@router.post("/market/profile/upgrade")
async def upgrade_tariff_with_payment(
    tariff: str = Form(...),
    receipt: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade market tariff — submit payment receipt for admin approval"""
    # Validate tariff
    try:
        target_tariff = MarketTariff(tariff)
    except ValueError:
        raise HTTPException(status_code=400, detail="Noto'g'ri tarif turi")

    if target_tariff == MarketTariff.FREE:
        raise HTTPException(status_code=400, detail="Free tarifga o'tish mumkin emas")

    # Check if user already has group-granted tariff
    group_plan = await MarketService.check_group_subscription(db, current_user.id)
    if group_plan and target_tariff == MarketTariff.STUDENT_PRO:
        raise HTTPException(
            status_code=400,
            detail="Guruh obunangiz orqali Student Pro tarifi allaqachon faol. Faqat Premium tarifga o'tish mumkin."
        )

    # Check for existing pending payment
    existing = await db.execute(
        select(MarketTariffPayment).where(
            MarketTariffPayment.user_id == current_user.id,
            MarketTariffPayment.status == "pending"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Sizda allaqachon kutilayotgan to'lov mavjud. Admin tasdiqlashini kuting."
        )

    # Determine amount based on tariff
    tariff_prices = {
        MarketTariff.STUDENT_PRO: 29000,
        MarketTariff.PREMIUM: 79000,
    }
    amount = tariff_prices.get(target_tariff, 0)

    # Save receipt file
    upload_dir = f"uploads/market_receipts/{current_user.id}"
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
    payment = MarketTariffPayment(
        user_id=current_user.id,
        tariff=target_tariff,
        amount=amount,
        status="pending",
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
        tariff_label = "Student Pro" if target_tariff == MarketTariff.STUDENT_PRO else "Premium"
        for aid in admin_ids:
            notif = Notification(
                user_id=aid,
                title="Yangi market tarif to'lovi 💰",
                message=f"{current_user.name} — {tariff_label} tarifi uchun {amount:,} so'm to'lov cheki yubordi. Tekshiring!",
                type=NotificationType.INFO,
                priority=NotificationPriority.HIGH,
            )
            db.add(notif)
        await db.commit()
    except Exception as e:
        logger.error(f"Market tariff notification error: {e}")

    return {
        "id": payment.id,
        "status": "pending",
        "message": "To'lov cheki yuborildi. Admin tasdiqlashini kuting."
    }


@router.get("/market/tariff-payments")
async def list_tariff_payments(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List market tariff payments (admin sees all, user sees own)"""
    query = select(MarketTariffPayment)
    count_query = select(func.count(MarketTariffPayment.id))

    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        query = query.where(MarketTariffPayment.user_id == current_user.id)
        count_query = count_query.where(MarketTariffPayment.user_id == current_user.id)

    if status:
        query = query.where(MarketTariffPayment.status == status)
        count_query = count_query.where(MarketTariffPayment.status == status)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(MarketTariffPayment.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    payments = result.scalars().all()

    items = []
    for p in payments:
        user_result = await db.execute(select(User.name).where(User.id == p.user_id))
        user_name = user_result.scalar() or "?"

        items.append({
            "id": p.id,
            "user_id": p.user_id,
            "user_name": user_name,
            "tariff": p.tariff.value if hasattr(p.tariff, 'value') else p.tariff,
            "amount": p.amount,
            "status": p.status,
            "receipt_file": p.receipt_file,
            "receipt_filename": p.receipt_filename,
            "admin_note": p.admin_note,
            "approved_by": p.approved_by,
            "approved_at": p.approved_at.isoformat() if p.approved_at else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.patch("/market/tariff-payments/{payment_id}")
async def action_tariff_payment(
    payment_id: int,
    action: str = Query(..., pattern="^(approved|rejected)$"),
    admin_note: Optional[str] = Query(None),
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Super admin: approve or reject a market tariff payment"""
    result = await db.execute(
        select(MarketTariffPayment).where(MarketTariffPayment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")

    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Bu to'lov allaqachon ko'rib chiqilgan")

    payment.status = action
    payment.admin_note = admin_note
    payment.approved_by = current_user.id
    payment.approved_at = now_tashkent()

    if action == "approved":
        # Activate tariff for user
        profile = await MarketService.get_or_create_profile(db, payment.user_id)
        profile.tariff = payment.tariff
        profile.tariff_expires_at = now_tashkent() + timedelta(days=30)

        # Notify user
        tariff_label = "Student Pro" if payment.tariff == MarketTariff.STUDENT_PRO else "Premium"
        notif = Notification(
            user_id=payment.user_id,
            title=f"Market tarifi faollashtirildi ✅",
            message=f"{tariff_label} tarifi 30 kunga faollashtirildi! Endi e'lon qo'yishingiz mumkin.",
            type=NotificationType.SUCCESS,
            priority=NotificationPriority.HIGH,
            sender_id=current_user.id,
        )
        db.add(notif)
    else:
        # Notify user about rejection
        notif = Notification(
            user_id=payment.user_id,
            title="Market tarif to'lovi rad etildi ❌",
            message=f"To'lov chekingiz rad etildi. Sabab: {admin_note or 'ko`rsatilmagan'}",
            type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
            sender_id=current_user.id,
        )
        db.add(notif)

    await db.commit()

    return {"id": payment.id, "status": payment.status, "message": "To'lov yangilandi"}


@router.get("/market/tariff-receipt/{payment_id}")
async def get_tariff_receipt(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tariff payment receipt file"""
    result = await db.execute(
        select(MarketTariffPayment).where(MarketTariffPayment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")

    # Only admin/superadmin or the user themselves can see receipt
    if payment.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    if not payment.receipt_file or not os.path.exists(payment.receipt_file):
        raise HTTPException(status_code=404, detail="Chek topilmadi")

    from fastapi.responses import FileResponse
    return FileResponse(payment.receipt_file)


@router.get("/market/tariff-prices")
async def get_tariff_prices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tariff prices and card info for payment"""
    # Get card info from subscription settings
    settings_result = await db.execute(select(SubscriptionSettings).limit(1))
    settings = settings_result.scalar_one_or_none()

    return {
        "tariffs": {
            "student_pro": {"price": 29000, "label": "Student Pro", "duration_days": 30},
            "premium": {"price": 79000, "label": "Premium", "duration_days": 30},
        },
        "card_number": settings.card_number if settings else None,
        "card_holder": settings.card_holder if settings else None,
    }


# ==================== Listings ====================

@router.get("/market/listings", response_model=dict)
async def list_listings(
    category: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    seller_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Browse marketplace listings"""
    # Admin/superadmin can see all statuses; regular users only see active
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        # Admin: if no specific status, show all
        if status is None:
            status = ''  # empty means all
    else:
        if seller_id != current_user.id:
            status = "active"

    listings, total = await MarketService.get_listings(
        db, category=category, search=search,
        status=status, seller_id=seller_id,
        page=page, page_size=page_size
    )

    # Enrich with seller info
    items = []
    for listing in listings:
        seller_result = await db.execute(
            select(User.name).where(User.id == listing.seller_id)
        )
        seller_name = seller_result.scalar_one_or_none()

        profile_result = await db.execute(
            select(UserMarketProfile.seller_rating).where(
                UserMarketProfile.user_id == listing.seller_id
            )
        )
        seller_rating = profile_result.scalar_one_or_none()

        item = {
            "id": listing.id,
            "seller_id": listing.seller_id,
            "seller_name": seller_name,
            "seller_rating": seller_rating or 0,
            "title": listing.title,
            "description": listing.description,
            "category": listing.category.value if hasattr(listing.category, 'value') else listing.category,
            "subject": listing.subject,
            "direction": listing.direction,
            "price": listing.price,
            "currency": listing.currency,
            "delivery_days": listing.delivery_days,
            "max_revisions": listing.max_revisions,
            "status": listing.status.value if hasattr(listing.status, 'value') else listing.status,
            "rejection_reason": listing.rejection_reason,
            "views": listing.views,
            "orders_count": listing.orders_count,
            "images": listing.images,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
            "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
        }
        items.append(item)

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/market/listings/{listing_id}")
async def get_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get listing detail and increment views"""
    listing = await MarketService.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(404, "E'lon topilmadi")

    # Only owner/admin can see non-active
    if listing.status != ListingStatus.ACTIVE:
        if listing.seller_id != current_user.id and current_user.role not in [
            UserRole.ADMIN, UserRole.SUPERADMIN
        ]:
            raise HTTPException(404, "E'lon topilmadi")

    # Increment view count
    if listing.seller_id != current_user.id:
        await MarketService.increment_views(db, listing_id)
        await db.commit()

    # Enrich
    seller_result = await db.execute(
        select(User.name).where(User.id == listing.seller_id)
    )
    seller_name = seller_result.scalar_one_or_none()

    profile_result = await db.execute(
        select(UserMarketProfile.seller_rating).where(
            UserMarketProfile.user_id == listing.seller_id
        )
    )
    seller_rating = profile_result.scalar_one_or_none()

    return {
        "id": listing.id,
        "seller_id": listing.seller_id,
        "seller_name": seller_name,
        "seller_rating": seller_rating or 0,
        "title": listing.title,
        "description": listing.description,
        "category": listing.category.value if hasattr(listing.category, 'value') else listing.category,
        "subject": listing.subject,
        "direction": listing.direction,
        "price": listing.price,
        "currency": listing.currency,
        "delivery_days": listing.delivery_days,
        "max_revisions": listing.max_revisions,
        "status": listing.status.value if hasattr(listing.status, 'value') else listing.status,
        "rejection_reason": listing.rejection_reason,
        "views": listing.views,
        "orders_count": listing.orders_count,
        "images": listing.images,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
    }


@router.post("/market/listings")
async def create_listing(
    data: ListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new service listing"""
    listing = await MarketService.create_listing(db, current_user.id, data.dict())
    await db.commit()
    return {"id": listing.id, "status": listing.status.value, "message": "E'lon moderatsiyaga yuborildi"}


@router.put("/market/listings/{listing_id}")
async def update_listing(
    listing_id: int,
    data: ListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update own listing"""
    listing = await MarketService.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(404, "E'lon topilmadi")
    if listing.seller_id != current_user.id:
        raise HTTPException(403, "Ruxsat yo'q")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(listing, key, value)

    # Re-submit for moderation if active
    if listing.status == ListingStatus.ACTIVE:
        listing.status = ListingStatus.PENDING

    await db.commit()
    return {"message": "E'lon yangilandi", "status": listing.status.value}


@router.delete("/market/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a listing"""
    listing = await MarketService.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(404, "E'lon topilmadi")
    if listing.seller_id != current_user.id and current_user.role not in [
        UserRole.ADMIN, UserRole.SUPERADMIN
    ]:
        raise HTTPException(403, "Ruxsat yo'q")

    listing.status = ListingStatus.ARCHIVED
    await db.commit()
    return {"message": "E'lon arxivlandi"}


@router.post("/market/listings/{listing_id}/moderate")
async def moderate_listing(
    listing_id: int,
    data: ListingModerationAction,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin: approve or reject a listing"""
    listing = await MarketService.moderate_listing(
        db, listing_id, current_user.id, data.action, data.reason
    )
    await db.commit()
    return {"message": f"E'lon {'tasdiqlandi' if data.action == 'approve' else 'rad etildi'}"}


# ==================== Orders ====================

@router.post("/market/orders")
async def create_order(
    listing_id: int = Form(...),
    requirements: Optional[str] = Form(None),
    deadline_days: Optional[int] = Form(None),
    receipt: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Place an order for a listing with payment receipt"""
    # Save receipt file
    upload_dir = f"uploads/order_receipts/{current_user.id}"
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

    order_data = {
        "listing_id": listing_id,
        "requirements": requirements,
        "deadline_days": deadline_days,
    }
    order = await MarketService.create_order(db, current_user.id, order_data)

    # Save receipt info on the order
    order.payment_receipt = filepath
    order.payment_receipt_filename = receipt.filename

    await db.commit()

    # Notify seller about new order with payment
    try:
        listing = await MarketService.get_listing(db, listing_id)
        if listing:
            notif = Notification(
                user_id=listing.seller_id,
                title="Yangi buyurtma keldi! 🛒",
                message=f"{current_user.name} sizning \"{listing.title}\" xizmatingizga buyurtma berdi. To'lov chekini tekshiring va qabul qiling.",
                type=NotificationType.INFO,
                priority=NotificationPriority.HIGH,
                sender_id=current_user.id,
            )
            db.add(notif)
            await db.commit()
    except Exception as e:
        logger.error(f"Order notification error: {e}")

    return {
        "id": order.id,
        "status": order.status.value if hasattr(order.status, 'value') else order.status,
        "amount": order.amount,
        "message": "Buyurtma yaratildi. To'lov cheki yuborildi."
    }


@router.get("/market/orders", response_model=dict)
async def list_orders(
    role: str = Query("all", pattern="^(all|buyer|seller)$"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's orders"""
    orders, total = await MarketService.get_orders(
        db, current_user.id, role=role, status=status,
        page=page, page_size=page_size
    )

    items = []
    for order in orders:
        buyer_name = (await db.execute(
            select(User.name).where(User.id == order.buyer_id)
        )).scalar_one_or_none()
        seller_name = (await db.execute(
            select(User.name).where(User.id == order.seller_id)
        )).scalar_one_or_none()

        items.append({
            "id": order.id,
            "listing_id": order.listing_id,
            "buyer_id": order.buyer_id,
            "seller_id": order.seller_id,
            "buyer_name": buyer_name,
            "seller_name": seller_name,
            "title": order.title,
            "description": order.description,
            "amount": order.amount,
            "commission_rate": order.commission_rate,
            "commission_amount": order.commission_amount,
            "seller_amount": order.seller_amount,
            "deadline": order.deadline.isoformat() if order.deadline else None,
            "status": order.status.value if hasattr(order.status, 'value') else order.status,
            "revision_count": order.revision_count,
            "max_revisions": order.max_revisions,
            "delivery_file": order.delivery_file,
            "delivery_note": order.delivery_note,
            "payment_receipt": order.payment_receipt,
            "payment_receipt_filename": order.payment_receipt_filename,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/market/orders/all", response_model=dict)
async def list_all_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin: list all marketplace orders"""
    orders, total = await MarketService.get_all_orders(
        db, status=status, page=page, page_size=page_size
    )

    items = []
    for order in orders:
        buyer_name = (await db.execute(
            select(User.name).where(User.id == order.buyer_id)
        )).scalar_one_or_none()
        seller_name = (await db.execute(
            select(User.name).where(User.id == order.seller_id)
        )).scalar_one_or_none()

        items.append({
            "id": order.id,
            "listing_id": order.listing_id,
            "buyer_id": order.buyer_id,
            "seller_id": order.seller_id,
            "buyer_name": buyer_name,
            "seller_name": seller_name,
            "title": order.title,
            "amount": order.amount,
            "commission_amount": order.commission_amount,
            "status": order.status.value if hasattr(order.status, 'value') else order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/market/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order detail"""
    order = await MarketService.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")

    # Access check
    if (order.buyer_id != current_user.id and order.seller_id != current_user.id
            and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        raise HTTPException(403, "Ruxsat yo'q")

    buyer_name = (await db.execute(
        select(User.name).where(User.id == order.buyer_id)
    )).scalar_one_or_none()
    seller_name = (await db.execute(
        select(User.name).where(User.id == order.seller_id)
    )).scalar_one_or_none()

    # Escrow info
    from app.models.market import EscrowTransaction
    escrow_result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.order_id == order_id)
    )
    escrow = escrow_result.scalar_one_or_none()

    return {
        "id": order.id,
        "listing_id": order.listing_id,
        "buyer_id": order.buyer_id,
        "seller_id": order.seller_id,
        "buyer_name": buyer_name,
        "seller_name": seller_name,
        "title": order.title,
        "description": order.description,
        "requirements": order.requirements,
        "amount": order.amount,
        "commission_rate": order.commission_rate,
        "commission_amount": order.commission_amount,
        "seller_amount": order.seller_amount,
        "deadline": order.deadline.isoformat() if order.deadline else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "status": order.status.value if hasattr(order.status, 'value') else order.status,
        "revision_count": order.revision_count,
        "max_revisions": order.max_revisions,
        "delivery_file": order.delivery_file,
        "delivery_note": order.delivery_note,
        "payment_receipt": order.payment_receipt,
        "payment_receipt_filename": order.payment_receipt_filename,
        "buyer_rating": order.buyer_rating,
        "buyer_review": order.buyer_review,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "escrow": {
            "amount": escrow.amount,
            "commission": escrow.commission,
            "seller_payout": escrow.seller_payout,
            "status": escrow.status.value if hasattr(escrow.status, 'value') else escrow.status,
        } if escrow else None,
    }


@router.get("/market/orders/{order_id}/receipt")
async def get_order_receipt(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order payment receipt file"""
    order = await MarketService.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")

    if (order.buyer_id != current_user.id and order.seller_id != current_user.id
            and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        raise HTTPException(403, "Ruxsat yo'q")

    if not order.payment_receipt or not os.path.exists(order.payment_receipt):
        raise HTTPException(404, "To'lov cheki topilmadi")

    from fastapi.responses import FileResponse
    return FileResponse(order.payment_receipt)


@router.post("/market/orders/{order_id}/accept")
async def accept_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Seller accepts an order"""
    order = await MarketService.accept_order(db, order_id, current_user.id)
    await db.commit()
    return {"message": "Buyurtma qabul qilindi", "status": order.status.value}


@router.post("/market/orders/{order_id}/deliver")
async def deliver_order(
    order_id: int,
    data: OrderDelivery,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Seller delivers work"""
    order = await MarketService.deliver_order(
        db, order_id, current_user.id,
        delivery_note=data.delivery_note,
        delivery_file=data.delivery_file
    )
    await db.commit()
    return {"message": "Ish topshirildi", "status": order.status.value}


@router.post("/market/orders/{order_id}/accept-delivery")
async def accept_delivery(
    order_id: int,
    data: OrderAcceptance,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Buyer accepts delivery — releases escrow"""
    order = await MarketService.accept_delivery(
        db, order_id, current_user.id,
        rating=data.rating, review=data.review
    )
    await db.commit()
    return {"message": "Ish qabul qilindi! Pul sotuvchiga o'tkazildi.", "status": order.status.value}


@router.post("/market/orders/{order_id}/revision")
async def request_revision(
    order_id: int,
    data: OrderRevisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Buyer requests revision"""
    order = await MarketService.request_revision(
        db, order_id, current_user.id, data.reason
    )
    await db.commit()
    return {"message": "Qayta ko'rib chiqish so'raldi", "status": order.status.value}


@router.post("/market/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending order"""
    order = await MarketService.cancel_order(db, order_id, current_user.id)
    await db.commit()
    return {"message": "Buyurtma bekor qilindi", "status": order.status.value}


# ==================== Disputes ====================

@router.post("/market/orders/{order_id}/dispute")
async def open_dispute(
    order_id: int,
    data: DisputeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Open a dispute for an order"""
    dispute = await MarketService.open_dispute(
        db, order_id, current_user.id, data.reason
    )
    await db.commit()
    return {"id": dispute.id, "message": "Nizo ochildi. Admin ko'rib chiqadi."}


@router.get("/market/disputes")
async def list_disputes(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin: list all disputes"""
    disputes, total = await MarketService.get_disputes(
        db, status=status, page=page, page_size=page_size
    )

    items = []
    for d in disputes:
        order = await MarketService.get_order(db, d.order_id)
        opener_name = (await db.execute(
            select(User.name).where(User.id == d.opened_by)
        )).scalar_one_or_none()

        buyer_name = None
        seller_name = None
        if order:
            buyer_name = (await db.execute(
                select(User.name).where(User.id == order.buyer_id)
            )).scalar_one_or_none()
            seller_name = (await db.execute(
                select(User.name).where(User.id == order.seller_id)
            )).scalar_one_or_none()

        items.append({
            "id": d.id,
            "order_id": d.order_id,
            "order_title": order.title if order else None,
            "opened_by": d.opened_by,
            "opener_name": opener_name,
            "buyer_name": buyer_name,
            "seller_name": seller_name,
            "reason": d.reason,
            "status": d.status.value if hasattr(d.status, 'value') else d.status,
            "buyer_refund": d.buyer_refund,
            "seller_payout": d.seller_payout,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/market/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: int,
    data: DisputeResolve,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Super admin: resolve a dispute"""
    dispute = await MarketService.resolve_dispute(
        db, dispute_id, current_user.id,
        resolution=data.resolution,
        note=data.note,
        buyer_percent=data.buyer_percent
    )
    await db.commit()
    return {"message": "Nizo hal qilindi", "status": dispute.status.value}


# ==================== Chat (REST) ====================

@router.get("/market/orders/{order_id}/messages")
async def get_messages(
    order_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat messages for an order"""
    order = await MarketService.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")

    # Access check
    if (order.buyer_id != current_user.id and order.seller_id != current_user.id
            and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        raise HTTPException(403, "Ruxsat yo'q")

    messages, total = await MarketService.get_messages(
        db, order_id, current_user.id, page=page, page_size=page_size
    )
    await db.commit()

    items = []
    for msg in messages:
        sender_name = (await db.execute(
            select(User.name).where(User.id == msg.sender_id)
        )).scalar_one_or_none()

        items.append({
            "id": msg.id,
            "order_id": msg.order_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_name,
            "content": msg.content,
            "message_type": msg.message_type,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "is_system": msg.is_system,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/market/orders/{order_id}/messages")
async def send_message(
    order_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in order chat"""
    order = await MarketService.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")

    if (order.buyer_id != current_user.id and order.seller_id != current_user.id
            and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        raise HTTPException(403, "Ruxsat yo'q")

    msg = await MarketService.send_message(
        db, order_id, current_user.id,
        content=data.content,
        message_type=data.message_type,
        file_url=data.file_url,
        file_name=data.file_name
    )
    await db.commit()

    # Broadcast via WebSocket
    sender_name_result = await db.execute(
        select(User.name).where(User.id == current_user.id)
    )
    sender_name = sender_name_result.scalar_one_or_none()

    ws_message = {
        "type": "new_message",
        "data": {
            "id": msg.id,
            "order_id": msg.order_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_name,
            "content": msg.content,
            "message_type": msg.message_type,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "is_system": msg.is_system,
            "is_read": False,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
    }
    await manager.send_to_order(order_id, ws_message, exclude_user=current_user.id)

    return ws_message["data"]


@router.get("/market/unread")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unread messages count"""
    count = await MarketService.get_unread_count(db, current_user.id)
    return {"unread": count}


# ==================== Payouts ====================

@router.post("/market/payouts")
async def request_payout(
    data: PayoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Request a payout to card"""
    payout = await MarketService.request_payout(
        db, current_user.id, data.amount, data.card_number
    )
    await db.commit()
    return {"id": payout.id, "message": "To'lov so'rovi yuborildi (24-72 soat)"}


@router.get("/market/payouts")
async def list_payouts(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Super admin: list all payouts"""
    result = await db.execute(
        select(SellerPayout).order_by(SellerPayout.requested_at.desc()).limit(100)
    )
    payouts = result.scalars().all()

    items = []
    for p in payouts:
        user_name = (await db.execute(
            select(User.name).where(User.id == p.user_id)
        )).scalar_one_or_none()
        items.append({
            "id": p.id,
            "user_id": p.user_id,
            "user_name": user_name,
            "amount": p.amount,
            "card_number": p.card_number,
            "status": p.status.value if hasattr(p.status, 'value') else p.status,
            "requested_at": p.requested_at.isoformat() if p.requested_at else None,
            "processed_at": p.processed_at.isoformat() if p.processed_at else None,
        })

    return {"items": items}


@router.post("/market/payouts/{payout_id}/process")
async def process_payout(
    payout_id: int,
    action: str = Query(..., pattern="^(complete|fail)$"),
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Super admin: process a payout"""
    payout = await MarketService.process_payout(db, payout_id, action)
    await db.commit()
    return {"message": "To'lov qayta ishlandi", "status": payout.status.value}


# ==================== Stats ====================

@router.get("/market/stats")
async def get_market_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin/Super: marketplace dashboard stats"""
    stats = await MarketService.get_stats(db)
    return stats


# ==================== WebSocket ====================

@router.websocket("/market/ws/{order_id}")
async def websocket_chat(
    websocket: WebSocket,
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time order chat"""
    # Authenticate from query param
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = int(payload.get("sub", 0))
    if not user_id:
        await websocket.close(code=4001)
        return

    # Verify user has access to this order
    order = await MarketService.get_order(db, order_id)
    if not order:
        await websocket.close(code=4004)
        return

    # Get user role
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        await websocket.close(code=4001)
        return

    if (order.buyer_id != user_id and order.seller_id != user_id
            and user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        await websocket.close(code=4003)
        return

    await manager.connect(websocket, order_id, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue

                # Block links/phones
                import re
                link_patterns = [
                    r'https?://\S+', r'www\.\S+', r't\.me/\S+',
                    r'@\w+', r'\+?\d{10,}'
                ]
                blocked = False
                for pattern in link_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        await websocket.send_json({
                            "type": "error",
                            "message": "Havolalar va telefon raqamlari taqiqlangan"
                        })
                        blocked = True
                        break

                if blocked:
                    continue

                msg = await MarketService.send_message(
                    db, order_id, user_id,
                    content=content,
                    message_type=data.get("message_type", "text"),
                    file_url=data.get("file_url"),
                    file_name=data.get("file_name")
                )
                await db.commit()

                sender_name = user.name

                ws_msg = {
                    "type": "new_message",
                    "data": {
                        "id": msg.id,
                        "order_id": msg.order_id,
                        "sender_id": msg.sender_id,
                        "sender_name": sender_name,
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "file_url": msg.file_url,
                        "file_name": msg.file_name,
                        "is_system": False,
                        "is_read": False,
                        "created_at": msg.created_at.isoformat(),
                    }
                }

                # Send to all including sender
                await manager.send_to_order(order_id, ws_msg)

            elif data.get("type") == "typing":
                await manager.send_to_order(order_id, {
                    "type": "typing",
                    "user_id": user_id,
                    "user_name": user.name
                }, exclude_user=user_id)

            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(order_id, user_id)
    except Exception as e:
        logger.error(f"WS error: {e}")
        manager.disconnect(order_id, user_id)
