"""
Subscription Check Middleware
==============================
Checks if the subscribed group has an active Plus+ subscription
that includes bot access. If not, blocks bot usage for that group.
"""
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy import select
import logging
from datetime import datetime, timedelta
from bot.config import now_tashkent

from bot.database import async_session, Subscription
from bot.services.api_client import UniControlAPI
from bot.config import settings

logger = logging.getLogger(__name__)

# Cache subscription check results to avoid excessive API calls
# Format: {group_id: {"has_access": bool, "message": str, "checked_at": datetime}}
_subscription_cache: Dict[int, Dict] = {}
CACHE_TTL = timedelta(minutes=5)  # Cache for 5 minutes


class SubscriptionCheckMiddleware(BaseMiddleware):
    """
    Middleware that checks if the group's UniControl subscription
    includes bot access (Plus plan or above).
    
    If subscription is Start or missing, blocks bot commands.
    """

    def __init__(self):
        self.api = UniControlAPI()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user and chat info from event
        user = None
        chat_id = None

        if isinstance(event, Message):
            user = event.from_user
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat_id = event.message.chat.id if event.message else None

        if not user or not chat_id:
            return await handler(event, data)

        # Skip for admin users
        admin_ids_list = settings.admin_ids or []
        if user.id in admin_ids_list:
            return await handler(event, data)

        # Skip for /start and /help commands (always allowed)
        if isinstance(event, Message) and event.text:
            cmd = event.text.strip().split()[0].lower()
            if cmd in ("/start", "/help"):
                return await handler(event, data)

        # Get the subscription for this chat
        group_id = None
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.chat_id == chat_id,
                    Subscription.is_active == True
                )
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                group_id = subscription.group_id

        # If no subscription (not linked to any group), allow — other handlers will handle it
        if not group_id:
            return await handler(event, data)

        # Check subscription with cache
        has_access, block_message = await self._check_subscription(group_id)

        if has_access:
            # Store subscription info in data for handlers to use
            data["subscription_plan"] = _subscription_cache.get(group_id, {}).get("plan_type")
            return await handler(event, data)
        else:
            # Block access
            block_text = (
                "🔒 <b>Bot xizmati bloklangan</b>\n\n"
                f"{block_message}\n\n"
                "📋 <b>Bot xizmati quyidagi rejalarda mavjud:</b>\n"
                "• 💎 <b>Plus</b> — 40,000 so'm/oy\n"
                "• 🏆 <b>Pro</b> — 50,000 so'm/oy\n"
                "• 👑 <b>Unlimited</b> — 55,000 so'm/oy\n\n"
                "💡 <i>Obunani yangilash uchun UniControl platformasiga kiring.</i>"
            )

            if isinstance(event, Message):
                await event.answer(block_text, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("Bot xizmati bloklangan!", show_alert=True)
                if event.message:
                    await event.message.answer(block_text, parse_mode="HTML")

            return  # Block handler execution

    async def _check_subscription(self, group_id: int) -> tuple:
        """
        Check subscription with caching.
        Returns (has_access: bool, block_message: str)
        """
        now = now_tashkent()

        # Check cache
        cached = _subscription_cache.get(group_id)
        if cached and (now - cached["checked_at"]) < CACHE_TTL:
            return cached["has_access"], cached.get("message", "")

        # Call API
        try:
            result = await self.api.check_bot_subscription(group_id)
            if result:
                has_access = result.get("has_access", False)
                message = result.get("message", "Obuna topilmadi")
                plan_type = result.get("plan_type")

                _subscription_cache[group_id] = {
                    "has_access": has_access,
                    "message": message,
                    "plan_type": plan_type,
                    "checked_at": now
                }
                return has_access, message
            else:
                # API error — allow access to avoid blocking on errors
                logger.warning(f"Subscription check API returned None for group {group_id}")
                return True, ""
        except Exception as e:
            logger.error(f"Subscription check error for group {group_id}: {e}")
            # On error, allow access (fail-open)
            return True, ""


def clear_subscription_cache(group_id: Optional[int] = None):
    """Clear subscription cache for a group or all groups"""
    if group_id:
        _subscription_cache.pop(group_id, None)
    else:
        _subscription_cache.clear()
