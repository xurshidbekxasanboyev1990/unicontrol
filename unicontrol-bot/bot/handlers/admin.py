"""
Admin Panel Handler
===================
Full admin panel for bot management.
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func, update, delete
from datetime import datetime, timedelta
from bot.config import now_tashkent, today_tashkent
import logging
import asyncio

from bot.config import settings
from bot.database import (
    async_session, 
    BotUser, 
    MandatoryChannel, 
    BotSettings,
    Broadcast,
    AdminLog,
    Subscription
)
from bot.keyboards.admin import (
    get_admin_main_menu,
    get_admin_stats_keyboard,
    get_admin_broadcast_keyboard,
    get_admin_channels_keyboard,
    get_channel_detail_keyboard,
    get_admin_settings_keyboard,
    get_admin_users_keyboard,
    get_user_detail_keyboard,
    get_broadcast_confirm_keyboard,
    get_broadcast_progress_keyboard,
    get_admin_logs_keyboard
)

router = Router(name="admin")
logger = logging.getLogger(__name__)


# ==================== FSM States ====================

class AdminStates(StatesGroup):
    """Admin panel FSM states"""
    # Broadcast
    waiting_broadcast_message = State()
    waiting_broadcast_buttons = State()
    
    # Channels
    waiting_channel_id = State()
    
    # Users
    waiting_user_search = State()
    waiting_ban_reason = State()
    waiting_user_message = State()
    
    # Settings
    waiting_welcome_message = State()
    waiting_maintenance_message = State()
    waiting_subscribe_message = State()


# ==================== Helpers ====================

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin_ids = settings.admin_ids or []
    return user_id in admin_ids


async def log_admin_action(
    admin_id: int,
    admin_username: str,
    action: str,
    details: dict = None,
    target_type: str = None,
    target_id: int = None
):
    """Log admin action to database"""
    async with async_session() as session:
        log = AdminLog(
            admin_id=admin_id,
            admin_username=admin_username,
            action=action,
            action_details=details,
            target_type=target_type,
            target_id=target_id
        )
        session.add(log)
        await session.commit()


async def get_or_create_settings() -> dict:
    """Get bot settings, create if not exists"""
    async with async_session() as session:
        result = await session.execute(select(BotSettings).where(BotSettings.id == 1))
        settings_obj = result.scalar_one_or_none()
        
        if not settings_obj:
            settings_obj = BotSettings(id=1)
            session.add(settings_obj)
            await session.commit()
            await session.refresh(settings_obj)
        
        return {
            "is_active": settings_obj.is_active,
            "maintenance_mode": settings_obj.maintenance_mode,
            "maintenance_message": settings_obj.maintenance_message,
            "force_subscribe": settings_obj.force_subscribe,
            "subscribe_message": settings_obj.subscribe_message,
            "welcome_message": settings_obj.welcome_message,
            "notifications_enabled": settings_obj.notifications_enabled,
            "rate_limit_enabled": settings_obj.rate_limit_enabled,
            "rate_limit_messages": settings_obj.rate_limit_messages
        }


# ==================== Main Admin Command ====================

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda admin huquqi yo'q.")
        return
    
    await message.answer(
        "🛠 <b>Admin Panel</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu()
    )


# ==================== Statistics ====================

@router.callback_query(F.data == "admin:stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Show statistics menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    # Get quick stats
    async with async_session() as session:
        # Total users
        total_users = await session.scalar(select(func.count(BotUser.id)))
        
        # Active today
        today = today_tashkent()
        active_today = await session.scalar(
            select(func.count(BotUser.id)).where(
                func.date(BotUser.last_active) == today
            )
        )
        
        # Subscriptions
        total_subs = await session.scalar(
            select(func.count(Subscription.id)).where(Subscription.is_active == True)
        )
        
        # Blocked users
        blocked = await session.scalar(
            select(func.count(BotUser.id)).where(BotUser.is_blocked == True)
        )
    
    text = f"""
📊 <b>Statistika</b>

👥 <b>Foydalanuvchilar:</b>
├ Jami: {total_users or 0}
├ Bugun faol: {active_today or 0}
└ Bloklangan: {blocked or 0}

📋 <b>Obunalar:</b>
└ Faol obunalar: {total_subs or 0}
"""
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_stats_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:stats:"))
async def callback_admin_stats_period(callback: CallbackQuery):
    """Show statistics for specific period"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    period = callback.data.split(":")[-1]
    
    # Calculate date range
    now = now_tashkent()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "Bugun"
    elif period == "week":
        start_date = now - timedelta(days=7)
        period_name = "So'nggi 7 kun"
    else:  # month
        start_date = now - timedelta(days=30)
        period_name = "So'nggi 30 kun"
    
    async with async_session() as session:
        # New users in period
        new_users = await session.scalar(
            select(func.count(BotUser.id)).where(
                BotUser.first_seen >= start_date
            )
        )
        
        # Active users in period
        active_users = await session.scalar(
            select(func.count(BotUser.id)).where(
                BotUser.last_active >= start_date
            )
        )
        
        # New subscriptions
        new_subs = await session.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.subscribed_at >= start_date
            )
        )
    
    text = f"""
📈 <b>Statistika - {period_name}</b>

👥 <b>Foydalanuvchilar:</b>
├ Yangi: {new_users or 0}
└ Faol: {active_users or 0}

📋 <b>Obunalar:</b>
└ Yangi: {new_subs or 0}
"""
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_stats_keyboard()
    )
    await callback.answer()


# ==================== Broadcast ====================

@router.callback_query(F.data == "admin:broadcast")
async def callback_admin_broadcast(callback: CallbackQuery):
    """Show broadcast menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>E'lon yuborish</b>\n\n"
        "Barcha foydalanuvchilarga xabar yuborish uchun\n"
        "quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_admin_broadcast_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast:new")
async def callback_broadcast_new(callback: CallbackQuery, state: FSMContext):
    """Start new broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_broadcast_message)
    
    await callback.message.edit_text(
        "📢 <b>Yangi e'lon</b>\n\n"
        "E'lon matnini yuboring.\n"
        "Rasm, video yoki fayl ham yuborishingiz mumkin.\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Process broadcast message"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "❌ E'lon bekor qilindi.",
            reply_markup=get_admin_broadcast_keyboard()
        )
        return
    
    # Get message content
    message_text = message.text or message.caption or ""
    message_type = "text"
    media_file_id = None
    
    if message.photo:
        message_type = "photo"
        media_file_id = message.photo[-1].file_id
    elif message.video:
        message_type = "video"
        media_file_id = message.video.file_id
    elif message.document:
        message_type = "document"
        media_file_id = message.document.file_id
    
    # Get total users
    async with async_session() as session:
        total_users = await session.scalar(
            select(func.count(BotUser.id)).where(
                BotUser.is_blocked == False,
                BotUser.is_banned == False
            )
        )
        
        # Create broadcast record
        broadcast = Broadcast(
            message_text=message_text,
            message_type=message_type,
            media_file_id=media_file_id,
            total_users=total_users or 0,
            created_by=message.from_user.id,
            status="pending"
        )
        session.add(broadcast)
        await session.commit()
        await session.refresh(broadcast)
        broadcast_id = broadcast.id
    
    await state.clear()
    
    await message.answer(
        f"📢 <b>E'lon tayyor</b>\n\n"
        f"📝 Turi: {message_type}\n"
        f"👥 Qabul qiluvchilar: {total_users or 0} ta\n\n"
        f"Yuborishni tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=get_broadcast_confirm_keyboard(broadcast_id)
    )


@router.callback_query(F.data.startswith("admin:broadcast:confirm:"))
async def callback_broadcast_confirm(callback: CallbackQuery, bot: Bot):
    """Confirm and start broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    broadcast_id = int(callback.data.split(":")[-1])
    
    # Get broadcast
    async with async_session() as session:
        result = await session.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        broadcast = result.scalar_one_or_none()
        
        if not broadcast:
            await callback.answer("E'lon topilmadi", show_alert=True)
            return
        
        # Update status
        broadcast.status = "sending"
        broadcast.started_at = now_tashkent()
        await session.commit()
    
    await callback.message.edit_text(
        "📢 <b>E'lon yuborilmoqda...</b>\n\n"
        "⏳ Iltimos, kuting...",
        parse_mode="HTML",
        reply_markup=get_broadcast_progress_keyboard(broadcast_id)
    )
    await callback.answer()
    
    # Start broadcast in background
    asyncio.create_task(
        send_broadcast(bot, broadcast_id, callback.message)
    )


async def send_broadcast(bot: Bot, broadcast_id: int, status_message: Message):
    """Send broadcast to all users"""
    async with async_session() as session:
        # Get broadcast
        result = await session.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        broadcast = result.scalar_one_or_none()
        
        if not broadcast:
            return
        
        # Get all active users
        result = await session.execute(
            select(BotUser.telegram_id).where(
                BotUser.is_blocked == False,
                BotUser.is_banned == False
            )
        )
        user_ids = [row[0] for row in result.fetchall()]
    
    sent = 0
    failed = 0
    blocked = 0
    
    for i, user_id in enumerate(user_ids):
        # Check if cancelled
        async with async_session() as session:
            result = await session.execute(
                select(Broadcast.status).where(Broadcast.id == broadcast_id)
            )
            status = result.scalar_one_or_none()
            if status == "cancelled":
                break
        
        try:
            if broadcast.message_type == "text":
                await bot.send_message(user_id, broadcast.message_text)
            elif broadcast.message_type == "photo":
                await bot.send_photo(user_id, broadcast.media_file_id, caption=broadcast.message_text)
            elif broadcast.message_type == "video":
                await bot.send_video(user_id, broadcast.media_file_id, caption=broadcast.message_text)
            elif broadcast.message_type == "document":
                await bot.send_document(user_id, broadcast.media_file_id, caption=broadcast.message_text)
            sent += 1
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked += 1
                # Mark user as blocked
                async with async_session() as session:
                    await session.execute(
                        update(BotUser).where(BotUser.telegram_id == user_id).values(is_blocked=True)
                    )
                    await session.commit()
            else:
                failed += 1
        
        # Update progress every 50 users
        if (i + 1) % 50 == 0:
            async with async_session() as session:
                await session.execute(
                    update(Broadcast).where(Broadcast.id == broadcast_id).values(
                        sent_count=sent,
                        failed_count=failed,
                        blocked_count=blocked
                    )
                )
                await session.commit()
            
            try:
                await status_message.edit_text(
                    f"📢 <b>E'lon yuborilmoqda...</b>\n\n"
                    f"📊 <b>Jarayon:</b> {i+1}/{len(user_ids)}\n"
                    f"✅ Yuborildi: {sent}\n"
                    f"❌ Xato: {failed}\n"
                    f"🚫 Bloklangan: {blocked}",
                    parse_mode="HTML",
                    reply_markup=get_broadcast_progress_keyboard(broadcast_id)
                )
            except:
                pass
        
        # Rate limit
        await asyncio.sleep(0.05)
    
    # Final update
    async with async_session() as session:
        await session.execute(
            update(Broadcast).where(Broadcast.id == broadcast_id).values(
                status="completed",
                sent_count=sent,
                failed_count=failed,
                blocked_count=blocked,
                completed_at=now_tashkent()
            )
        )
        await session.commit()
    
    try:
        await status_message.edit_text(
            f"✅ <b>E'lon yuborildi!</b>\n\n"
            f"📊 <b>Natija:</b>\n"
            f"✅ Yuborildi: {sent}\n"
            f"❌ Xato: {failed}\n"
            f"🚫 Bloklangan: {blocked}\n"
            f"👥 Jami: {len(user_ids)}",
            parse_mode="HTML"
        )
    except:
        pass


@router.callback_query(F.data.startswith("admin:broadcast:stop:"))
async def callback_broadcast_stop(callback: CallbackQuery):
    """Stop ongoing broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    broadcast_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        await session.execute(
            update(Broadcast).where(Broadcast.id == broadcast_id).values(
                status="cancelled"
            )
        )
        await session.commit()
    
    await callback.answer("E'lon to'xtatildi", show_alert=True)


# ==================== Mandatory Channels ====================

@router.callback_query(F.data == "admin:channels")
async def callback_admin_channels(callback: CallbackQuery):
    """Show mandatory channels list"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    async with async_session() as session:
        result = await session.execute(
            select(MandatoryChannel).order_by(MandatoryChannel.priority)
        )
        channels = result.scalars().all()
    
    channels_list = [
        {
            "id": ch.id,
            "channel_title": ch.channel_title,
            "is_active": ch.is_active
        }
        for ch in channels
    ]
    
    text = "📺 <b>Majburiy obuna kanallari</b>\n\n"
    if channels:
        text += f"Jami: {len(channels)} ta kanal\n\n"
        text += "Kanal sozlamalarini o'zgartirish uchun ustiga bosing."
    else:
        text += "Hozircha kanal qo'shilmagan.\n\n"
        text += "➕ tugmasini bosib kanal qo'shing."
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_channels_keyboard(channels_list)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:channel:add")
async def callback_channel_add(callback: CallbackQuery, state: FSMContext):
    """Add new mandatory channel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_channel_id)
    
    await callback.message.edit_text(
        "📺 <b>Kanal qo'shish</b>\n\n"
        "Kanal ID sini yoki @username ni yuboring.\n"
        "Bot kanalda admin bo'lishi kerak.\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_channel_id)
async def process_channel_id(message: Message, state: FSMContext, bot: Bot):
    """Process channel ID input"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return
    
    channel_input = message.text.strip()
    
    try:
        # Try to get channel info
        if channel_input.startswith("@"):
            chat = await bot.get_chat(channel_input)
        else:
            chat = await bot.get_chat(int(channel_input))
        
        # Check if bot is admin
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        if bot_member.status not in ("administrator", "creator"):
            await message.answer(
                "⚠️ Bot bu kanalda admin emas.\n"
                "Botni kanalga admin qilib qaytadan urinib ko'ring."
            )
            return
        
        # Save channel
        async with async_session() as session:
            # Check if exists
            result = await session.execute(
                select(MandatoryChannel).where(MandatoryChannel.channel_id == chat.id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                await message.answer("⚠️ Bu kanal allaqachon qo'shilgan.")
                await state.clear()
                return
            
            channel = MandatoryChannel(
                channel_id=chat.id,
                channel_username=chat.username,
                channel_title=chat.title,
                channel_url=f"https://t.me/{chat.username}" if chat.username else None,
                added_by=message.from_user.id
            )
            session.add(channel)
            await session.commit()
        
        await state.clear()
        
        await log_admin_action(
            message.from_user.id,
            message.from_user.username,
            "add_channel",
            {"channel_id": chat.id, "channel_title": chat.title},
            "channel",
            chat.id
        )
        
        await message.answer(
            f"✅ <b>Kanal qo'shildi!</b>\n\n"
            f"📺 {chat.title}\n"
            f"🆔 {chat.id}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await message.answer(
            f"❌ Xatolik: {str(e)}\n\n"
            "Kanal ID yoki username to'g'ri ekanligini tekshiring."
        )


@router.callback_query(F.data.startswith("admin:channel:") & ~F.data.contains("toggle") & ~F.data.contains("delete") & ~F.data.contains("add"))
async def callback_channel_detail(callback: CallbackQuery):
    """Show channel details"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    channel_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(MandatoryChannel).where(MandatoryChannel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
    
    if not channel:
        await callback.answer("Kanal topilmadi", show_alert=True)
        return
    
    status = "✅ Faol" if channel.is_active else "❌ O'chirilgan"
    
    text = f"""
📺 <b>Kanal ma'lumotlari</b>

📝 Nomi: {channel.channel_title}
🆔 ID: {channel.channel_id}
👤 Username: @{channel.channel_username or "yo'q"}
📊 Holat: {status}
📅 Qo'shilgan: {channel.added_at.strftime("%d.%m.%Y %H:%M")}
"""
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_channel_detail_keyboard(channel.id, channel.is_active)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:channel:toggle:"))
async def callback_channel_toggle(callback: CallbackQuery):
    """Toggle channel active status"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    channel_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(MandatoryChannel).where(MandatoryChannel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if channel:
            channel.is_active = not channel.is_active
            await session.commit()
            status = "yoqildi ✅" if channel.is_active else "o'chirildi ❌"
            await callback.answer(f"Kanal {status}")
            
            # Refresh view
            await callback_channel_detail(callback)


@router.callback_query(F.data.startswith("admin:channel:delete:"))
async def callback_channel_delete(callback: CallbackQuery):
    """Delete channel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    channel_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        await session.execute(
            delete(MandatoryChannel).where(MandatoryChannel.id == channel_id)
        )
        await session.commit()
    
    await log_admin_action(
        callback.from_user.id,
        callback.from_user.username,
        "delete_channel",
        {"channel_id": channel_id},
        "channel",
        channel_id
    )
    
    await callback.answer("Kanal o'chirildi ✅")
    
    # Go back to channels list
    await callback_admin_channels(callback)


# ==================== Bot Settings ====================

@router.callback_query(F.data == "admin:settings")
async def callback_admin_settings(callback: CallbackQuery):
    """Show bot settings"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    settings_data = await get_or_create_settings()
    
    await callback.message.edit_text(
        "⚙️ <b>Bot sozlamalari</b>\n\n"
        "Sozlamalarni o'zgartirish uchun ustiga bosing:",
        parse_mode="HTML",
        reply_markup=get_admin_settings_keyboard(settings_data)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:settings:toggle:"))
async def callback_settings_toggle(callback: CallbackQuery):
    """Toggle boolean settings"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    setting_name = callback.data.split(":")[-1]
    
    async with async_session() as session:
        result = await session.execute(select(BotSettings).where(BotSettings.id == 1))
        settings_obj = result.scalar_one_or_none()
        
        if settings_obj:
            current_value = getattr(settings_obj, setting_name, False)
            setattr(settings_obj, setting_name, not current_value)
            settings_obj.updated_by = callback.from_user.id
            await session.commit()
    
    await log_admin_action(
        callback.from_user.id,
        callback.from_user.username,
        f"toggle_{setting_name}",
        {"new_value": not current_value}
    )
    
    # Refresh settings view
    await callback_admin_settings(callback)


@router.callback_query(F.data.startswith("admin:settings:edit:"))
async def callback_settings_edit(callback: CallbackQuery, state: FSMContext):
    """Edit text settings"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    setting_type = callback.data.split(":")[-1]
    
    state_map = {
        "welcome": AdminStates.waiting_welcome_message,
        "maintenance": AdminStates.waiting_maintenance_message,
        "subscribe": AdminStates.waiting_subscribe_message
    }
    
    title_map = {
        "welcome": "Xush kelibsiz xabari",
        "maintenance": "Ta'mirlash xabari",
        "subscribe": "Obuna xabari"
    }
    
    await state.set_state(state_map[setting_type])
    await state.update_data(setting_type=setting_type)
    
    await callback.message.edit_text(
        f"✏️ <b>{title_map[setting_type]}</b>\n\n"
        "Yangi matnni yuboring.\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_welcome_message)
@router.message(AdminStates.waiting_maintenance_message)
@router.message(AdminStates.waiting_subscribe_message)
async def process_settings_message(message: Message, state: FSMContext):
    """Process settings text input"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return
    
    data = await state.get_data()
    setting_type = data.get("setting_type")
    
    field_map = {
        "welcome": "welcome_message",
        "maintenance": "maintenance_message",
        "subscribe": "subscribe_message"
    }
    
    async with async_session() as session:
        result = await session.execute(select(BotSettings).where(BotSettings.id == 1))
        settings_obj = result.scalar_one_or_none()
        
        if settings_obj:
            setattr(settings_obj, field_map[setting_type], message.text)
            settings_obj.updated_by = message.from_user.id
            await session.commit()
    
    await state.clear()
    
    await message.answer(
        f"✅ {setting_type.capitalize()} xabari saqlandi!",
        parse_mode="HTML"
    )


# ==================== Users Management ====================

@router.callback_query(F.data == "admin:users")
async def callback_admin_users(callback: CallbackQuery):
    """Show users management menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 <b>Foydalanuvchilar boshqaruvi</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_admin_users_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users:search")
async def callback_users_search(callback: CallbackQuery, state: FSMContext):
    """Start user search"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_user_search)
    
    await callback.message.edit_text(
        "🔍 <b>Foydalanuvchi izlash</b>\n\n"
        "Foydalanuvchi ID yoki @username ni yuboring.\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_user_search)
async def process_user_search(message: Message, state: FSMContext):
    """Process user search"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return
    
    search_query = message.text.strip().lstrip("@")
    
    async with async_session() as session:
        # Try to find by ID or username
        if search_query.isdigit():
            result = await session.execute(
                select(BotUser).where(BotUser.telegram_id == int(search_query))
            )
        else:
            result = await session.execute(
                select(BotUser).where(BotUser.username.ilike(f"%{search_query}%"))
            )
        
        user = result.scalar_one_or_none()
    
    await state.clear()
    
    if not user:
        await message.answer(
            "❌ Foydalanuvchi topilmadi.\n\n"
            "ID yoki username to'g'ri ekanligini tekshiring."
        )
        return
    
    status = "🚫 Bloklangan" if user.is_banned else ("⚠️ Botni bloklagan" if user.is_blocked else "✅ Faol")
    
    text = f"""
👤 <b>Foydalanuvchi ma'lumotlari</b>

🆔 ID: <code>{user.telegram_id}</code>
👤 Ism: {user.first_name or ""} {user.last_name or ""}
📝 Username: @{user.username or "yo'q"}
📊 Holat: {status}
📅 Ro'yxatdan o'tgan: {user.first_seen.strftime("%d.%m.%Y %H:%M")}
🕐 So'nggi faollik: {user.last_active.strftime("%d.%m.%Y %H:%M")}
"""
    
    if user.is_banned and user.ban_reason:
        text += f"\n📝 Bloklash sababi: {user.ban_reason}"
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_user_detail_keyboard(user.telegram_id, user.is_banned)
    )


@router.callback_query(F.data.startswith("admin:user:ban:"))
async def callback_user_ban(callback: CallbackQuery, state: FSMContext):
    """Ban user"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    await state.set_state(AdminStates.waiting_ban_reason)
    await state.update_data(ban_user_id=user_id)
    
    await callback.message.edit_text(
        "🚫 <b>Foydalanuvchini bloklash</b>\n\n"
        "Bloklash sababini yuboring.\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_ban_reason)
async def process_ban_reason(message: Message, state: FSMContext):
    """Process ban reason"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return
    
    data = await state.get_data()
    user_id = data.get("ban_user_id")
    
    async with async_session() as session:
        await session.execute(
            update(BotUser).where(BotUser.telegram_id == user_id).values(
                is_banned=True,
                ban_reason=message.text
            )
        )
        await session.commit()
    
    await state.clear()
    
    await log_admin_action(
        message.from_user.id,
        message.from_user.username,
        "ban_user",
        {"reason": message.text},
        "user",
        user_id
    )
    
    await message.answer(
        f"✅ Foydalanuvchi bloklandi!\n\n"
        f"🆔 ID: {user_id}\n"
        f"📝 Sabab: {message.text}"
    )


@router.callback_query(F.data.startswith("admin:user:unban:"))
async def callback_user_unban(callback: CallbackQuery):
    """Unban user"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        await session.execute(
            update(BotUser).where(BotUser.telegram_id == user_id).values(
                is_banned=False,
                ban_reason=None
            )
        )
        await session.commit()
    
    await log_admin_action(
        callback.from_user.id,
        callback.from_user.username,
        "unban_user",
        {},
        "user",
        user_id
    )
    
    await callback.answer("Foydalanuvchi blokdan chiqarildi ✅", show_alert=True)


# ==================== Logs ====================

@router.callback_query(F.data == "admin:logs")
async def callback_admin_logs(callback: CallbackQuery):
    """Show logs menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📋 <b>Admin loglar</b>\n\n"
        "Admin harakatlar tarixi:",
        parse_mode="HTML",
        reply_markup=get_admin_logs_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:logs:recent")
async def callback_logs_recent(callback: CallbackQuery):
    """Show recent logs"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    async with async_session() as session:
        result = await session.execute(
            select(AdminLog).order_by(AdminLog.created_at.desc()).limit(20)
        )
        logs = result.scalars().all()
    
    if not logs:
        await callback.answer("Loglar yo'q", show_alert=True)
        return
    
    text = "📋 <b>So'nggi loglar</b>\n\n"
    
    for log in logs:
        text += f"• {log.created_at.strftime('%d.%m %H:%M')} - "
        text += f"@{log.admin_username or log.admin_id}: "
        text += f"{log.action}\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_logs_keyboard()
    )
    await callback.answer()


# ==================== Navigation ====================

@router.callback_query(F.data.startswith("admin:back:"))
async def callback_admin_back(callback: CallbackQuery):
    """Handle back navigation in admin panel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Admin emas", show_alert=True)
        return
    
    destination = callback.data.split(":")[-1]
    
    if destination == "main":
        await callback.message.edit_text(
            "🛠 <b>Admin Panel</b>\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            parse_mode="HTML",
            reply_markup=get_admin_main_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "admin:close")
async def callback_admin_close(callback: CallbackQuery):
    """Close admin panel"""
    await callback.message.delete()
    await callback.answer()
