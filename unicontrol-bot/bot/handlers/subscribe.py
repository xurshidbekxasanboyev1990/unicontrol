from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, update
import logging
from datetime import datetime
from bot.config import now_tashkent

from bot.services import UniControlAPI, AttendanceFormatter
from bot.keyboards import get_confirm_keyboard, get_settings_keyboard, get_unsubscribe_confirm_keyboard
from bot.database import async_session, Subscription
from bot.middlewares.subscription_check import clear_subscription_cache

router = Router(name="subscribe")
logger = logging.getLogger(__name__)

api = UniControlAPI()


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """
    Handle /subscribe command.
    Usage: /subscribe KI_25-09
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "⚠️ <b>Guruh kodini kiriting</b>\n\n"
            "Foydalanish: <code>/subscribe KI_25-09</code>\n\n"
            "💡 <i>Guruh kodini bilmasangiz, /search buyrug'i bilan qidiring.</i>",
            parse_mode="HTML"
        )
        return
    
    group_code = args[1].strip().upper()
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_title = message.chat.title or message.from_user.full_name
    
    # Check if already subscribed
    async with async_session() as session:
        result = await session.execute(
            select(Subscription).where(
                Subscription.chat_id == chat_id,
                Subscription.is_active == True
            )
        )
        existing = result.scalar_one_or_none()
    
    if existing:
        if existing.group_code == group_code:
            await message.answer(
                f"✅ Bu chat allaqachon <b>{group_code}</b> guruhiga obuna.\n\n"
                f"📋 Davomatni ko'rish: /attendance\n"
                f"⚙️ Sozlamalar: /settings",
                parse_mode="HTML"
            )
            return
        else:
            # Ask to replace
            await message.answer(
                f"⚠️ Bu chat allaqachon <b>{existing.group_code}</b> guruhiga obuna.\n\n"
                f"<b>{group_code}</b> ga almashtirishni xohlaysizmi?",
                parse_mode="HTML",
                reply_markup=get_confirm_keyboard(
                    action="resubscribe",
                    data=group_code,
                    confirm_text="✅ Ha, almashtirish",
                    cancel_text="❌ Yo'q"
                )
            )
            return
    
    # Verify group exists
    await perform_subscription(message, group_code, chat_id, chat_type, chat_title)


async def perform_subscription(
    message: Message,
    group_code: str,
    chat_id: int,
    chat_type: str,
    chat_title: str,
    user_id: int = None
):
    """Perform actual subscription"""
    try:
        # Verify group exists
        group = await api.get_group_by_code(group_code)
        
        if not group:
            await message.answer(
                f"❌ <b>{group_code}</b> guruh topilmadi.\n\n"
                "💡 <i>To'g'ri kod kiritganingizni tekshiring.\n"
                "Guruh kodini /search buyrug'i bilan qidiring.</i>",
                parse_mode="HTML"
            )
            return False
        
        # Check if group has bot-level subscription (Plus+)
        group_id = group.get("id")
        if group_id:
            sub_check = await api.check_bot_subscription(group_id)
            if sub_check and not sub_check.get("has_access", False):
                block_msg = sub_check.get("message", "Obuna topilmadi")
                await message.answer(
                    f"🔒 <b>Bot xizmati mavjud emas</b>\n\n"
                    f"<b>{group_code}</b> guruhi uchun bot xizmati bloklangan.\n\n"
                    f"📌 <i>{block_msg}</i>\n\n"
                    "💡 <i>Obunani faollashtirish uchun Super Admin ga murojaat qiling.\n"
                    "Admin guruhlar sahifasidan obuna beradi.</i>",
                    parse_mode="HTML"
                )
                return False
        
        # Create or reactivate subscription
        async with async_session() as session:
            # Check for existing inactive subscription for this chat
            result = await session.execute(
                select(Subscription).where(Subscription.chat_id == chat_id)
            )
            existing_sub = result.scalar_one_or_none()
            
            if existing_sub:
                # Reactivate and update existing subscription
                existing_sub.group_code = group_code
                existing_sub.group_id = group.get("id")
                existing_sub.group_name = group.get("name")
                existing_sub.chat_title = chat_title
                existing_sub.chat_type = chat_type
                existing_sub.subscribed_by = user_id or message.from_user.id
                existing_sub.notify_late = True
                existing_sub.notify_absent = True
                existing_sub.notify_present = False
                existing_sub.is_active = True
                existing_sub.updated_at = now_tashkent()
            else:
                # Create new subscription
                subscription = Subscription(
                    chat_id=chat_id,
                    chat_title=chat_title,
                    chat_type=chat_type,
                    group_code=group_code,
                    group_id=group.get("id"),
                    group_name=group.get("name"),
                    subscribed_by=user_id or message.from_user.id,
                    notify_late=True,
                    notify_absent=True,
                    notify_present=False,
                    is_active=True
                )
                session.add(subscription)
            await session.commit()
        
        # Register with backend
        await api.register_telegram_chat(
            chat_id=chat_id,
            group_code=group_code,
            chat_type=chat_type,
            chat_title=chat_title
        )
        
        # Success message
        group_info = AttendanceFormatter.format_group_info(group)
        
        await message.answer(
            f"✅ <b>Obuna muvaffaqiyatli!</b>\n\n"
            f"{group_info}\n\n"
            f"📋 Endi bu chatga davomat xabarlari keladi.\n\n"
            f"<b>Buyruqlar:</b>\n"
            f"/attendance - Bugungi davomat\n"
            f"/settings - Xabar sozlamalari\n"
            f"/unsubscribe - Obunani bekor qilish",
            parse_mode="HTML"
        )
        return True
        
    except Exception as e:
        logger.error(f"Subscription error: {e}")
        await message.answer(
            "❌ Obuna jarayonida xatolik yuz berdi.\n"
            "Iltimos, keyinroq qayta urinib ko'ring.",
            parse_mode="HTML"
        )
        return False


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    """Handle /unsubscribe command"""
    chat_id = message.chat.id
    
    async with async_session() as session:
        result = await session.execute(
            select(Subscription).where(
                Subscription.chat_id == chat_id,
                Subscription.is_active == True
            )
        )
        subscription = result.scalar_one_or_none()
    
    if not subscription:
        await message.answer(
            "❌ Bu chat hech qaysi guruhga obuna emas.",
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        f"⚠️ <b>{subscription.group_code}</b> guruhidan obunani bekor qilishni tasdiqlaysizmi?\n\n"
        f"Endi davomat xabarlari kelmaydi.",
        parse_mode="HTML",
        reply_markup=get_unsubscribe_confirm_keyboard()
    )


@router.callback_query(F.data == "confirm:unsubscribe")
async def callback_confirm_unsubscribe(callback: CallbackQuery):
    """Confirm unsubscription"""
    chat_id = callback.message.chat.id
    
    try:
        async with async_session() as session:
            await session.execute(
                update(Subscription)
                .where(Subscription.chat_id == chat_id)
                .values(is_active=False, updated_at=now_tashkent())
            )
            await session.commit()
        
        # Unregister from backend
        await api.unregister_telegram_chat(chat_id)
        
        await callback.message.edit_text(
            "✅ <b>Obuna bekor qilindi</b>\n\n"
            "Endi davomat xabarlari kelmaydi.\n\n"
            "Qayta obuna bo'lish uchun: /subscribe [kod]",
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Unsubscribe error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)


@router.callback_query(F.data.startswith("subscribe:"))
async def callback_subscribe(callback: CallbackQuery):
    """Handle subscription from callback"""
    group_code = callback.data.split(":")[1]
    
    chat_id = callback.message.chat.id
    chat_type = callback.message.chat.type
    chat_title = callback.message.chat.title or callback.from_user.full_name
    user_id = callback.from_user.id
    
    # Check if already subscribed
    async with async_session() as session:
        result = await session.execute(
            select(Subscription).where(
                Subscription.chat_id == chat_id,
                Subscription.is_active == True
            )
        )
        existing = result.scalar_one_or_none()
    
    if existing:
        await callback.answer(
            f"Allaqachon {existing.group_code} ga obuna",
            show_alert=True
        )
        return
    
    await callback.answer("Obuna qilinmoqda...")
    
    # Delete current message and perform subscription
    await callback.message.delete()
    
    await perform_subscription(
        callback.message,
        group_code,
        chat_id,
        chat_type,
        chat_title,
        user_id
    )


@router.callback_query(F.data.startswith("confirm:resubscribe:"))
async def callback_resubscribe(callback: CallbackQuery):
    """Handle resubscription confirmation"""
    group_code = callback.data.split(":")[2]
    
    chat_id = callback.message.chat.id
    chat_type = callback.message.chat.type
    chat_title = callback.message.chat.title or callback.from_user.full_name
    user_id = callback.from_user.id
    
    try:
        # Deactivate old subscription
        async with async_session() as session:
            await session.execute(
                update(Subscription)
                .where(Subscription.chat_id == chat_id)
                .values(is_active=False, updated_at=now_tashkent())
            )
            await session.commit()
        
        await callback.answer("Almashtirilmoqda...")
        
        # Edit message instead of deleting (safe approach)
        await callback.message.edit_text(
            f"⏳ <b>{group_code}</b> guruhiga almashtirilmoqda...",
            parse_mode="HTML"
        )
        
        # Create new subscription — use a wrapper that sends new message
        class _MsgProxy:
            def __init__(self, msg):
                self._msg = msg
                self.chat = msg.chat
                self.from_user = callback.from_user
            async def answer(self, *a, **kw):
                return await self._msg.answer(*a, **kw)
        
        await perform_subscription(
            _MsgProxy(callback.message),
            group_code,
            chat_id,
            chat_type,
            chat_title,
            user_id
        )
        
    except Exception as e:
        logger.error(f"Resubscribe error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)


@router.callback_query(F.data.startswith("cancel:"))
async def callback_cancel(callback: CallbackQuery):
    """Handle cancel actions"""
    await callback.message.delete()
    await callback.answer("Bekor qilindi")


@router.callback_query(F.data.startswith("setting:"))
async def callback_setting_toggle(callback: CallbackQuery):
    """Toggle notification settings"""
    setting = callback.data.split(":")[1]
    chat_id = callback.message.chat.id
    
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.chat_id == chat_id,
                    Subscription.is_active == True
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                await callback.answer("Obuna topilmadi", show_alert=True)
                return
            
            # Toggle setting
            current_value = getattr(subscription, setting, False)
            setattr(subscription, setting, not current_value)
            subscription.updated_at = now_tashkent()
            
            await session.commit()
            
            # Update message
            text = f"""
⚙️ <b>Sozlamalar</b>

🏫 Guruh: <b>{subscription.group_code}</b>
📅 Obuna sanasi: {subscription.subscribed_at.strftime("%d.%m.%Y")}

<b>Xabar sozlamalari:</b>
"""
            keyboard = get_settings_keyboard({
                "notify_late": subscription.notify_late,
                "notify_absent": subscription.notify_absent,
                "notify_present": subscription.notify_present
            })
            
            await callback.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            status = "yoqildi ✅" if not current_value else "o'chirildi ❌"
            await callback.answer(f"Sozlama {status}")
            
    except Exception as e:
        logger.error(f"Settings error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
