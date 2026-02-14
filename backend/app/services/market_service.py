"""
UniControl - UniMarket Service
================================
Business logic for marketplace operations:
listings, orders, escrow, chat, disputes, payouts.
"""

from datetime import datetime, timedelta
from app.config import now_tashkent, today_tashkent
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from loguru import logger

from app.models.market import (
    UserMarketProfile, ServiceListing, MarketOrder,
    EscrowTransaction, MarketDispute, MarketMessage, SellerPayout,
    MarketTariff, ListingStatus, MarketOrderStatus, EscrowStatus,
    DisputeStatus, PayoutStatus, ListingCategory, TARIFF_LIMITS
)
from app.models.user import User
from app.models.student import Student
from app.models.subscription import GroupSubscription, SubscriptionPlanType, SubscriptionStatus
from app.core.exceptions import APIException


class MarketService:
    """Service layer for UniMarket operations"""

    # ==================== Group Subscription Check ====================

    @staticmethod
    async def check_group_subscription(db: AsyncSession, user_id: int) -> Optional[str]:
        """
        Check if user's group has an active pro/unlimited subscription.
        Returns the plan_type if eligible, None otherwise.
        """
        from datetime import date as date_type

        # Find student by user_id
        result = await db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        student = result.scalar_one_or_none()
        if not student or not student.group_id:
            return None

        # Check group subscription - active + pro/unlimited
        today = today_tashkent()
        result = await db.execute(
            select(GroupSubscription).where(
                GroupSubscription.group_id == student.group_id,
                GroupSubscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.TRIAL.value
                ]),
                GroupSubscription.plan_type.in_([
                    SubscriptionPlanType.PRO.value,
                    SubscriptionPlanType.UNLIMITED.value
                ]),
                GroupSubscription.end_date >= today
            ).order_by(desc(GroupSubscription.end_date))
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            return subscription.plan_type
        return None

    # ==================== Profile ====================

    @staticmethod
    async def get_or_create_profile(db: AsyncSession, user_id: int) -> UserMarketProfile:
        """Get or create market profile for a user, with group subscription check"""
        result = await db.execute(
            select(UserMarketProfile).where(UserMarketProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = UserMarketProfile(user_id=user_id, tariff=MarketTariff.FREE)
            db.add(profile)
            await db.flush()

        # Check group subscription for auto tariff upgrade
        group_plan = await MarketService.check_group_subscription(db, user_id)
        if group_plan in [SubscriptionPlanType.PRO.value, SubscriptionPlanType.UNLIMITED.value]:
            # Auto-grant student_pro if group has pro/unlimited
            if profile.tariff == MarketTariff.FREE.value or profile.tariff == MarketTariff.FREE:
                profile.tariff = MarketTariff.STUDENT_PRO
                profile.tariff_expires_at = None  # No expiry — linked to group sub
                await db.flush()
            # Store the source info as a transient attribute (not in DB)
            profile._tariff_source = "group_subscription"
            profile._group_plan = group_plan
        else:
            profile._tariff_source = "individual"
            profile._group_plan = None

            # If tariff was set from group sub before but group sub expired, revert to free
            # Only revert if tariff_expires_at is None (meaning it was from group sub)
            if (profile.tariff == MarketTariff.STUDENT_PRO.value or profile.tariff == MarketTariff.STUDENT_PRO) \
                    and profile.tariff_expires_at is None:
                profile.tariff = MarketTariff.FREE
                await db.flush()

        return profile

    @staticmethod
    async def update_profile(
        db: AsyncSession, user_id: int,
        card_number: Optional[str] = None,
        card_holder: Optional[str] = None
    ) -> UserMarketProfile:
        profile = await MarketService.get_or_create_profile(db, user_id)
        if card_number is not None:
            profile.card_number = card_number
        if card_holder is not None:
            profile.card_holder = card_holder
        await db.flush()
        return profile

    @staticmethod
    async def upgrade_tariff(
        db: AsyncSession, user_id: int, tariff: MarketTariff
    ) -> UserMarketProfile:
        profile = await MarketService.get_or_create_profile(db, user_id)
        profile.tariff = tariff
        profile.tariff_expires_at = now_tashkent() + timedelta(days=30)
        await db.flush()
        return profile

    # ==================== Listings ====================

    @staticmethod
    async def create_listing(
        db: AsyncSession, user_id: int, data: dict
    ) -> ServiceListing:
        profile = await MarketService.get_or_create_profile(db, user_id)
        limits = TARIFF_LIMITS.get(MarketTariff(profile.tariff))

        if not limits or not limits["can_create_listing"]:
            raise APIException(
                status_code=403,
                detail="Sizning tarifingiz e'lon qo'yishga ruxsat bermaydi. Tarifni yangilang."
            )

        # Check active listings count
        result = await db.execute(
            select(func.count()).select_from(ServiceListing).where(
                ServiceListing.seller_id == user_id,
                ServiceListing.status.in_([ListingStatus.ACTIVE, ListingStatus.PENDING])
            )
        )
        active_count = result.scalar() or 0
        max_orders = limits["max_active_orders"]
        if active_count >= max_orders:
            raise APIException(
                status_code=400,
                detail=f"Maksimal {max_orders} ta faol e'lon. Limitga yetdingiz."
            )

        listing = ServiceListing(
            seller_id=user_id,
            seller_profile_id=profile.id,
            title=data["title"],
            description=data["description"],
            category=data["category"],
            subject=data.get("subject"),
            direction=data.get("direction"),
            price=data["price"],
            delivery_days=data.get("delivery_days", 3),
            max_revisions=data.get("max_revisions", 2),
            images=data.get("images"),
            status=ListingStatus.PENDING  # needs moderation
        )
        db.add(listing)
        await db.flush()
        return listing

    @staticmethod
    async def get_listings(
        db: AsyncSession,
        category: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        seller_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ServiceListing], int]:
        query = select(ServiceListing)
        count_query = select(func.count()).select_from(ServiceListing)

        filters = []
        if category:
            filters.append(ServiceListing.category == category)
        if status is not None and status != '':
            filters.append(ServiceListing.status == status)
        elif status is None:
            filters.append(ServiceListing.status == ListingStatus.ACTIVE)
        # status == '' means show all statuses (for admin)
        if seller_id:
            filters.append(ServiceListing.seller_id == seller_id)
        if search:
            filters.append(
                or_(
                    ServiceListing.title.ilike(f"%{search}%"),
                    ServiceListing.description.ilike(f"%{search}%")
                )
            )

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(ServiceListing.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        listings = result.scalars().all()
        return listings, total

    @staticmethod
    async def get_listing(db: AsyncSession, listing_id: int) -> Optional[ServiceListing]:
        result = await db.execute(
            select(ServiceListing).where(ServiceListing.id == listing_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def moderate_listing(
        db: AsyncSession, listing_id: int, moderator_id: int,
        action: str, reason: Optional[str] = None
    ) -> ServiceListing:
        listing = await MarketService.get_listing(db, listing_id)
        if not listing:
            raise APIException(status_code=404, detail="E'lon topilmadi")

        if action == "approve":
            listing.status = ListingStatus.ACTIVE
        elif action == "reject":
            listing.status = ListingStatus.REJECTED
            listing.rejection_reason = reason

        listing.moderated_by = moderator_id
        listing.moderated_at = now_tashkent()
        await db.flush()
        return listing

    @staticmethod
    async def increment_views(db: AsyncSession, listing_id: int):
        await db.execute(
            update(ServiceListing)
            .where(ServiceListing.id == listing_id)
            .values(views=ServiceListing.views + 1)
        )

    # ==================== Orders ====================

    @staticmethod
    async def create_order(
        db: AsyncSession, buyer_id: int, data: dict
    ) -> MarketOrder:
        listing = await MarketService.get_listing(db, data["listing_id"])
        if not listing:
            raise APIException(status_code=404, detail="E'lon topilmadi")
        if listing.status != ListingStatus.ACTIVE:
            raise APIException(status_code=400, detail="Bu e'lon faol emas")
        if listing.seller_id == buyer_id:
            raise APIException(status_code=400, detail="O'z e'loningizga buyurtma berolmaysiz")

        buyer_profile = await MarketService.get_or_create_profile(db, buyer_id)
        seller_profile = await MarketService.get_or_create_profile(db, listing.seller_id)

        # Check seller limits
        seller_limits = TARIFF_LIMITS.get(MarketTariff(seller_profile.tariff))
        if not seller_limits or not seller_limits["can_escrow"]:
            raise APIException(
                status_code=400,
                detail="Sotuvchining tarifi garant tizimini qo'llab-quvvatlamaydi"
            )

        # Check active orders limit
        active_result = await db.execute(
            select(func.count()).select_from(MarketOrder).where(
                MarketOrder.seller_id == listing.seller_id,
                MarketOrder.status.in_([
                    MarketOrderStatus.PENDING, MarketOrderStatus.ACCEPTED,
                    MarketOrderStatus.PAID, MarketOrderStatus.IN_PROGRESS
                ])
            )
        )
        active_count = active_result.scalar() or 0
        if active_count >= seller_limits["max_active_orders"]:
            raise APIException(
                status_code=400,
                detail="Sotuvchi maksimal faol buyurtmalar soniga yetgan"
            )

        # Amount check
        if listing.price > seller_limits["max_amount_per_order"]:
            raise APIException(
                status_code=400,
                detail="Buyurtma summasi tarif limitidan oshib ketdi"
            )

        commission_rate = seller_limits["commission_rate"]
        commission_amount = listing.price * commission_rate
        seller_amount = listing.price - commission_amount

        deadline = None
        if data.get("deadline_days"):
            deadline = now_tashkent() + timedelta(days=data["deadline_days"])
        elif listing.delivery_days:
            deadline = now_tashkent() + timedelta(days=listing.delivery_days)

        order = MarketOrder(
            listing_id=listing.id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            title=listing.title,
            description=data.get("description"),
            requirements=data.get("requirements"),
            amount=listing.price,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            seller_amount=seller_amount,
            deadline=deadline,
            max_revisions=listing.max_revisions,
            status=MarketOrderStatus.PENDING
        )
        db.add(order)
        await db.flush()

        # Create escrow hold
        escrow = EscrowTransaction(
            order_id=order.id,
            amount=listing.price,
            commission=commission_amount,
            seller_payout=seller_amount,
            status=EscrowStatus.ON_HOLD,
            paid_at=now_tashkent()
        )
        db.add(escrow)

        # Update listing stats
        listing.orders_count += 1

        # System message in chat
        system_msg = MarketMessage(
            order_id=order.id,
            sender_id=buyer_id,
            content=f"Buyurtma #{order.id} yaratildi. Pul garant tizimida saqlanmoqda.",
            message_type="text",
            is_system=True
        )
        db.add(system_msg)

        await db.flush()
        return order

    @staticmethod
    async def get_orders(
        db: AsyncSession, user_id: int,
        role: str = "all",  # buyer, seller, all
        status: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ) -> Tuple[List[MarketOrder], int]:
        query = select(MarketOrder)
        count_query = select(func.count()).select_from(MarketOrder)

        filters = []
        if role == "buyer":
            filters.append(MarketOrder.buyer_id == user_id)
        elif role == "seller":
            filters.append(MarketOrder.seller_id == user_id)
        else:
            filters.append(
                or_(MarketOrder.buyer_id == user_id, MarketOrder.seller_id == user_id)
            )

        if status:
            filters.append(MarketOrder.status == status)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total = (await db.execute(count_query)).scalar() or 0
        query = query.order_by(desc(MarketOrder.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        orders = result.scalars().all()
        return orders, total

    @staticmethod
    async def get_all_orders(
        db: AsyncSession,
        status: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ) -> Tuple[List[MarketOrder], int]:
        """Admin: get all orders"""
        query = select(MarketOrder)
        count_query = select(func.count()).select_from(MarketOrder)

        if status:
            query = query.where(MarketOrder.status == status)
            count_query = count_query.where(MarketOrder.status == status)

        total = (await db.execute(count_query)).scalar() or 0
        query = query.order_by(desc(MarketOrder.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        return result.scalars().all(), total

    @staticmethod
    async def get_order(db: AsyncSession, order_id: int) -> Optional[MarketOrder]:
        result = await db.execute(
            select(MarketOrder).where(MarketOrder.id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def accept_order(db: AsyncSession, order_id: int, seller_id: int) -> MarketOrder:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.seller_id != seller_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status != MarketOrderStatus.PENDING:
            raise APIException(status_code=400, detail="Buyurtmani qabul qilib bo'lmaydi")

        order.status = MarketOrderStatus.IN_PROGRESS
        await db.flush()

        # System message
        msg = MarketMessage(
            order_id=order_id, sender_id=seller_id,
            content="Sotuvchi buyurtmani qabul qildi. Ish boshlandi.",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return order

    @staticmethod
    async def deliver_order(
        db: AsyncSession, order_id: int, seller_id: int,
        delivery_note: Optional[str] = None,
        delivery_file: Optional[str] = None
    ) -> MarketOrder:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.seller_id != seller_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status not in [MarketOrderStatus.IN_PROGRESS, MarketOrderStatus.REVISION]:
            raise APIException(status_code=400, detail="Bu holatda topshirib bo'lmaydi")

        order.status = MarketOrderStatus.DELIVERED
        order.delivered_at = now_tashkent()
        order.delivery_note = delivery_note
        order.delivery_file = delivery_file
        await db.flush()

        msg = MarketMessage(
            order_id=order_id, sender_id=seller_id,
            content="Ish topshirildi. Xaridor tekshirishni kutmoqda.",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return order

    @staticmethod
    async def accept_delivery(
        db: AsyncSession, order_id: int, buyer_id: int,
        rating: Optional[int] = None, review: Optional[str] = None
    ) -> MarketOrder:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.buyer_id != buyer_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status != MarketOrderStatus.DELIVERED:
            raise APIException(status_code=400, detail="Buyurtma topshirilmagan")

        order.status = MarketOrderStatus.COMPLETED
        order.completed_at = now_tashkent()
        order.buyer_rating = rating
        order.buyer_review = review
        await db.flush()

        # Release escrow
        escrow_result = await db.execute(
            select(EscrowTransaction).where(EscrowTransaction.order_id == order_id)
        )
        escrow = escrow_result.scalar_one_or_none()
        if escrow:
            escrow.status = EscrowStatus.RELEASED
            escrow.released_at = now_tashkent()

        # Credit seller balance
        seller_profile = await MarketService.get_or_create_profile(db, order.seller_id)
        seller_profile.balance += order.seller_amount
        seller_profile.total_earned += order.seller_amount
        seller_profile.completed_orders_as_seller += 1

        # Update buyer stats
        buyer_profile = await MarketService.get_or_create_profile(db, buyer_id)
        buyer_profile.total_spent += order.amount
        buyer_profile.completed_orders_as_buyer += 1

        # Update seller rating
        if rating:
            total_ratings = seller_profile.completed_orders_as_seller
            seller_profile.seller_rating = (
                (seller_profile.seller_rating * (total_ratings - 1) + rating) / total_ratings
            )

        msg = MarketMessage(
            order_id=order_id, sender_id=buyer_id,
            content=f"Ish qabul qilindi! {'⭐' * (rating or 0)} Pul sotuvchiga o'tkazildi.",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return order

    @staticmethod
    async def request_revision(
        db: AsyncSession, order_id: int, buyer_id: int, reason: str
    ) -> MarketOrder:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.buyer_id != buyer_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status != MarketOrderStatus.DELIVERED:
            raise APIException(status_code=400, detail="Buyurtma topshirilmagan")
        if order.revision_count >= order.max_revisions:
            raise APIException(status_code=400, detail="Maksimal qayta ko'rib chiqish soniga yetdi")

        order.status = MarketOrderStatus.REVISION
        order.revision_count += 1
        await db.flush()

        msg = MarketMessage(
            order_id=order_id, sender_id=buyer_id,
            content=f"Qayta ko'rib chiqish so'raldi ({order.revision_count}/{order.max_revisions}): {reason}",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return order

    @staticmethod
    async def cancel_order(
        db: AsyncSession, order_id: int, user_id: int
    ) -> MarketOrder:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status not in [MarketOrderStatus.PENDING]:
            raise APIException(
                status_code=400,
                detail="Faqat kutilayotgan buyurtmalarni bekor qilish mumkin"
            )

        order.status = MarketOrderStatus.CANCELLED

        # Refund escrow
        escrow_result = await db.execute(
            select(EscrowTransaction).where(EscrowTransaction.order_id == order_id)
        )
        escrow = escrow_result.scalar_one_or_none()
        if escrow:
            escrow.status = EscrowStatus.REFUNDED
            escrow.refunded_at = now_tashkent()

        await db.flush()
        return order

    # ==================== Disputes ====================

    @staticmethod
    async def open_dispute(
        db: AsyncSession, order_id: int, user_id: int, reason: str
    ) -> MarketDispute:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise APIException(status_code=403, detail="Ruxsat yo'q")
        if order.status not in [
            MarketOrderStatus.IN_PROGRESS, MarketOrderStatus.DELIVERED, MarketOrderStatus.REVISION
        ]:
            raise APIException(status_code=400, detail="Bu holatda nizoni ochib bo'lmaydi")

        # Check existing dispute
        existing = await db.execute(
            select(MarketDispute).where(MarketDispute.order_id == order_id)
        )
        if existing.scalar_one_or_none():
            raise APIException(status_code=400, detail="Bu buyurtmada allaqachon nizo ochilgan")

        order.status = MarketOrderStatus.DISPUTED

        dispute = MarketDispute(
            order_id=order_id,
            opened_by=user_id,
            reason=reason,
            status=DisputeStatus.OPEN
        )
        db.add(dispute)

        msg = MarketMessage(
            order_id=order_id, sender_id=user_id,
            content=f"⚠️ Nizo ochildi: {reason}",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return dispute

    @staticmethod
    async def get_disputes(
        db: AsyncSession,
        status: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ) -> Tuple[List[MarketDispute], int]:
        query = select(MarketDispute)
        count_query = select(func.count()).select_from(MarketDispute)

        if status:
            query = query.where(MarketDispute.status == status)
            count_query = count_query.where(MarketDispute.status == status)

        total = (await db.execute(count_query)).scalar() or 0
        query = query.order_by(desc(MarketDispute.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        return result.scalars().all(), total

    @staticmethod
    async def resolve_dispute(
        db: AsyncSession, dispute_id: int, resolver_id: int,
        resolution: str, note: str, buyer_percent: Optional[float] = None
    ) -> MarketDispute:
        result = await db.execute(
            select(MarketDispute).where(MarketDispute.id == dispute_id)
        )
        dispute = result.scalar_one_or_none()
        if not dispute:
            raise APIException(status_code=404, detail="Nizo topilmadi")

        order = await MarketService.get_order(db, dispute.order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")

        escrow_result = await db.execute(
            select(EscrowTransaction).where(EscrowTransaction.order_id == order.id)
        )
        escrow = escrow_result.scalar_one_or_none()

        total_amount = order.amount if escrow else 0

        if resolution == "buyer":
            dispute.status = DisputeStatus.RESOLVED_BUYER
            dispute.buyer_refund = total_amount
            dispute.seller_payout = 0
            if escrow:
                escrow.status = EscrowStatus.REFUNDED
                escrow.refunded_at = now_tashkent()
            order.status = MarketOrderStatus.REFUNDED

        elif resolution == "seller":
            dispute.status = DisputeStatus.RESOLVED_SELLER
            dispute.buyer_refund = 0
            commission = order.commission_amount
            dispute.seller_payout = total_amount - commission
            if escrow:
                escrow.status = EscrowStatus.RELEASED
                escrow.released_at = now_tashkent()
            # Credit seller
            seller_profile = await MarketService.get_or_create_profile(db, order.seller_id)
            seller_profile.balance += dispute.seller_payout
            seller_profile.total_earned += dispute.seller_payout
            order.status = MarketOrderStatus.COMPLETED
            order.completed_at = now_tashkent()

        elif resolution == "split":
            pct = (buyer_percent or 50) / 100
            dispute.status = DisputeStatus.RESOLVED_SPLIT
            dispute.buyer_refund = total_amount * pct
            dispute.seller_payout = total_amount * (1 - pct) * (1 - order.commission_rate)
            if escrow:
                escrow.status = EscrowStatus.PARTIAL_RELEASE
                escrow.released_at = now_tashkent()
            seller_profile = await MarketService.get_or_create_profile(db, order.seller_id)
            seller_profile.balance += dispute.seller_payout
            order.status = MarketOrderStatus.COMPLETED
            order.completed_at = now_tashkent()

        dispute.resolved_by = resolver_id
        dispute.resolution_note = note
        dispute.resolved_at = now_tashkent()

        msg = MarketMessage(
            order_id=order.id, sender_id=resolver_id,
            content=f"🔨 Nizo hal qilindi: {note}",
            message_type="text", is_system=True
        )
        db.add(msg)
        await db.flush()
        return dispute

    # ==================== Chat ====================

    @staticmethod
    async def get_messages(
        db: AsyncSession, order_id: int, user_id: int,
        page: int = 1, page_size: int = 50
    ) -> Tuple[List[MarketMessage], int]:
        # Verify access
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")

        # buyer, seller, admin, or superadmin can view
        # (admin check done at route level)

        count_query = select(func.count()).select_from(MarketMessage).where(
            MarketMessage.order_id == order_id
        )
        total = (await db.execute(count_query)).scalar() or 0

        query = (
            select(MarketMessage)
            .where(MarketMessage.order_id == order_id)
            .order_by(MarketMessage.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        messages = result.scalars().all()

        # Mark unread messages as read
        await db.execute(
            update(MarketMessage).where(
                MarketMessage.order_id == order_id,
                MarketMessage.sender_id != user_id,
                MarketMessage.is_read == False
            ).values(is_read=True)
        )

        return messages, total

    @staticmethod
    async def send_message(
        db: AsyncSession, order_id: int, sender_id: int,
        content: str, message_type: str = "text",
        file_url: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> MarketMessage:
        order = await MarketService.get_order(db, order_id)
        if not order:
            raise APIException(status_code=404, detail="Buyurtma topilmadi")

        if order.status in [MarketOrderStatus.COMPLETED, MarketOrderStatus.CANCELLED, MarketOrderStatus.REFUNDED]:
            raise APIException(status_code=400, detail="Yakunlangan buyurtmada xabar yuborib bo'lmaydi")

        msg = MarketMessage(
            order_id=order_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            file_url=file_url,
            file_name=file_name
        )
        db.add(msg)
        await db.flush()
        return msg

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        """Get total unread messages for user across all orders"""
        # Get user's order IDs
        orders_result = await db.execute(
            select(MarketOrder.id).where(
                or_(MarketOrder.buyer_id == user_id, MarketOrder.seller_id == user_id)
            )
        )
        order_ids = [r[0] for r in orders_result.all()]
        if not order_ids:
            return 0

        result = await db.execute(
            select(func.count()).select_from(MarketMessage).where(
                MarketMessage.order_id.in_(order_ids),
                MarketMessage.sender_id != user_id,
                MarketMessage.is_read == False
            )
        )
        return result.scalar() or 0

    # ==================== Payouts ====================

    @staticmethod
    async def request_payout(
        db: AsyncSession, user_id: int, amount: float,
        card_number: Optional[str] = None
    ) -> SellerPayout:
        profile = await MarketService.get_or_create_profile(db, user_id)

        if amount > profile.balance:
            raise APIException(status_code=400, detail="Balansda yetarli mablag' yo'q")
        if amount <= 0:
            raise APIException(status_code=400, detail="Summa musbat bo'lishi kerak")

        card = card_number or profile.card_number
        if not card:
            raise APIException(status_code=400, detail="Karta raqami ko'rsatilmagan")

        profile.balance -= amount

        payout = SellerPayout(
            user_id=user_id,
            amount=amount,
            card_number=card,
            status=PayoutStatus.PENDING
        )
        db.add(payout)
        await db.flush()
        return payout

    @staticmethod
    async def process_payout(
        db: AsyncSession, payout_id: int, action: str
    ) -> SellerPayout:
        result = await db.execute(
            select(SellerPayout).where(SellerPayout.id == payout_id)
        )
        payout = result.scalar_one_or_none()
        if not payout:
            raise APIException(status_code=404, detail="To'lov topilmadi")

        if action == "complete":
            payout.status = PayoutStatus.COMPLETED
            payout.processed_at = now_tashkent()
        elif action == "fail":
            payout.status = PayoutStatus.FAILED
            payout.processed_at = now_tashkent()
            # Return funds to balance
            profile = await MarketService.get_or_create_profile(db, payout.user_id)
            profile.balance += payout.amount

        await db.flush()
        return payout

    # ==================== Stats (Admin) ====================

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """Get marketplace dashboard stats"""
        listings_total = (await db.execute(
            select(func.count()).select_from(ServiceListing)
        )).scalar() or 0
        listings_active = (await db.execute(
            select(func.count()).select_from(ServiceListing)
            .where(ServiceListing.status == ListingStatus.ACTIVE)
        )).scalar() or 0
        listings_pending = (await db.execute(
            select(func.count()).select_from(ServiceListing)
            .where(ServiceListing.status == ListingStatus.PENDING)
        )).scalar() or 0

        orders_total = (await db.execute(
            select(func.count()).select_from(MarketOrder)
        )).scalar() or 0
        orders_active = (await db.execute(
            select(func.count()).select_from(MarketOrder)
            .where(MarketOrder.status.in_([
                MarketOrderStatus.PENDING, MarketOrderStatus.ACCEPTED,
                MarketOrderStatus.PAID, MarketOrderStatus.IN_PROGRESS
            ]))
        )).scalar() or 0
        orders_completed = (await db.execute(
            select(func.count()).select_from(MarketOrder)
            .where(MarketOrder.status == MarketOrderStatus.COMPLETED)
        )).scalar() or 0
        orders_disputed = (await db.execute(
            select(func.count()).select_from(MarketOrder)
            .where(MarketOrder.status == MarketOrderStatus.DISPUTED)
        )).scalar() or 0

        escrow_held = (await db.execute(
            select(func.coalesce(func.sum(EscrowTransaction.amount), 0))
            .where(EscrowTransaction.status == EscrowStatus.ON_HOLD)
        )).scalar() or 0

        commission_earned = (await db.execute(
            select(func.coalesce(func.sum(MarketOrder.commission_amount), 0))
            .where(MarketOrder.status == MarketOrderStatus.COMPLETED)
        )).scalar() or 0

        total_payouts = (await db.execute(
            select(func.coalesce(func.sum(SellerPayout.amount), 0))
            .where(SellerPayout.status == PayoutStatus.COMPLETED)
        )).scalar() or 0

        total_users = (await db.execute(
            select(func.count()).select_from(UserMarketProfile)
        )).scalar() or 0
        pro_users = (await db.execute(
            select(func.count()).select_from(UserMarketProfile)
            .where(UserMarketProfile.tariff == MarketTariff.STUDENT_PRO)
        )).scalar() or 0
        premium_users = (await db.execute(
            select(func.count()).select_from(UserMarketProfile)
            .where(UserMarketProfile.tariff == MarketTariff.PREMIUM)
        )).scalar() or 0

        pending_payments = (await db.execute(
            select(func.count()).select_from(MarketOrder)
            .where(
                MarketOrder.payment_receipt.isnot(None),
                MarketOrder.payment_verified == False,
                MarketOrder.payment_rejected == False,
            )
        )).scalar() or 0

        return {
            "total_listings": listings_total,
            "active_listings": listings_active,
            "pending_listings": listings_pending,
            "total_orders": orders_total,
            "active_orders": orders_active,
            "completed_orders": orders_completed,
            "disputed_orders": orders_disputed,
            "open_disputes": orders_disputed,
            "pending_payments": pending_payments,
            "total_escrow_held": float(escrow_held),
            "total_commission_earned": float(commission_earned),
            "total_payouts": float(total_payouts),
            "total_users": total_users,
            "pro_users": pro_users,
            "premium_users": premium_users,
        }