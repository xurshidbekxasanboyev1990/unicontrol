"""
Force Subscribe Middleware
==========================
Checks if user is subscribed to mandatory channels.
"""
from typing import Any, Awaitable, Callable, Dict, List
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy import select
import logging

from bot.database import async_session, MandatoryChannel, BotSettings, BotUser
from bot.keyboards.admin import get_force_subscribe_keyboard
from bot.config import settings

logger = logging.getLogger(__name__)


class ForceSubscribeMiddleware(BaseMiddleware):
    """
    Middleware to check mandatory channel subscription.
    If user is not subscribed, blocks access until they subscribe.
    """
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Skip for admins
        admin_ids = settings.admin_ids or []
        if user.id in admin_ids:
            return await handler(event, data)
        
        # Skip for check_subscription callback
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)
        
        # Check if force subscribe is enabled
        async with async_session() as session:
            result = await session.execute(select(BotSettings).where(BotSettings.id == 1))
            bot_settings = result.scalar_one_or_none()
            
            if not bot_settings or not bot_settings.force_subscribe:
                return await handler(event, data)
            
            # Get mandatory channels
            result = await session.execute(
                select(MandatoryChannel).where(MandatoryChannel.is_active == True)
            )
            channels = result.scalars().all()
        
        if not channels:
            return await handler(event, data)
        
        # Check subscription to each channel
        not_subscribed = []
        for channel in channels:
            try:
                member = await self.bot.get_chat_member(
                    channel.channel_id,
                    user.id
                )
                if member.status in ("left", "kicked"):
                    not_subscribed.append({
                        "channel_id": channel.channel_id,
                        "channel_username": channel.channel_username,
                        "channel_title": channel.channel_title,
                        "channel_url": channel.channel_url
                    })
            except Exception as e:
                logger.error(f"Error checking subscription: {e}")
                # Skip this channel if check fails
                continue
        
        if not_subscribed:
            # User not subscribed - show message
            text = (
                "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            )
            for ch in not_subscribed:
                text += f"📺 {ch['channel_title']}\n"
            
            text += "\n✅ Obuna bo'lgandan so'ng \"Tekshirish\" tugmasini bosing."
            
            keyboard = get_force_subscribe_keyboard(not_subscribed)
            
            if isinstance(event, Message):
                await event.answer(text, parse_mode="HTML", reply_markup=keyboard)
            elif isinstance(event, CallbackQuery):
                await event.answer("Kanallarga obuna bo'ling!", show_alert=True)
                await event.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
            
            return None
        
        # User is subscribed - continue
        return await handler(event, data)


class MaintenanceModeMiddleware(BaseMiddleware):
    """
    Middleware to check maintenance mode.
    If maintenance is enabled, blocks all users except admins.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Skip for admins
        admin_ids = settings.admin_ids or []
        if user.id in admin_ids:
            return await handler(event, data)
        
        # Check maintenance mode
        async with async_session() as session:
            result = await session.execute(select(BotSettings).where(BotSettings.id == 1))
            bot_settings = result.scalar_one_or_none()
            
            if not bot_settings:
                return await handler(event, data)
            
            # Check if bot is disabled
            if not bot_settings.is_active:
                message = "🔴 Bot hozirda faol emas. Keyinroq qaytadan urinib ko'ring."
                if isinstance(event, Message):
                    await event.answer(message)
                elif isinstance(event, CallbackQuery):
                    await event.answer(message, show_alert=True)
                return None
            
            # Check maintenance mode
            if bot_settings.maintenance_mode:
                message = bot_settings.maintenance_message or (
                    "🔧 Bot texnik ishlar sababli vaqtinchalik to'xtatilgan.\n"
                    "Tez orada qaytamiz!"
                )
                if isinstance(event, Message):
                    await event.answer(message)
                elif isinstance(event, CallbackQuery):
                    await event.answer("🔧 Texnik ishlar", show_alert=True)
                return None
        
        return await handler(event, data)


class UserTrackingMiddleware(BaseMiddleware):
    """
    Middleware to track all users for statistics and broadcast.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            # Track user
            try:
                async with async_session() as session:
                    result = await session.execute(
                        select(BotUser).where(BotUser.telegram_id == user.id)
                    )
                    bot_user = result.scalar_one_or_none()
                    
                    if bot_user:
                        # Update existing user
                        bot_user.username = user.username
                        bot_user.first_name = user.first_name
                        bot_user.last_name = user.last_name
                        bot_user.language_code = user.language_code
                        bot_user.is_blocked = False  # User is active
                    else:
                        # Create new user
                        bot_user = BotUser(
                            telegram_id=user.id,
                            username=user.username,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            language_code=user.language_code
                        )
                        session.add(bot_user)
                    
                    await session.commit()
            except Exception as e:
                logger.error(f"Error tracking user: {e}")
        
        return await handler(event, data)


class BannedUserMiddleware(BaseMiddleware):
    """
    Middleware to check if user is banned.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Check if banned
        async with async_session() as session:
            result = await session.execute(
                select(BotUser).where(
                    BotUser.telegram_id == user.id,
                    BotUser.is_banned == True
                )
            )
            banned_user = result.scalar_one_or_none()
        
        if banned_user:
            message = "🚫 Siz botda bloklangansiz."
            if banned_user.ban_reason:
                message += f"\n📝 Sabab: {banned_user.ban_reason}"
            
            if isinstance(event, Message):
                await event.answer(message)
            elif isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
            
            return None
        
        return await handler(event, data)
