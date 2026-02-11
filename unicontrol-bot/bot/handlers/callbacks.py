from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging

from bot.keyboards import get_main_menu_keyboard, get_settings_keyboard
from bot.database import async_session, Subscription
from sqlalchemy import select

router = Router(name="callbacks")
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("menu:"))
async def callback_menu(callback: CallbackQuery):
    """Handle menu navigation callbacks"""
    action = callback.data.split(":")[1]
    
    if action == "search":
        await callback.message.edit_text(
            "🔍 <b>Guruh qidirish</b>\n\n"
            "Guruh kodini yoki nomini yozing:\n"
            "<i>Masalan: KI_25-09</i>\n\n"
            "Yoki /search buyrug'idan foydalaning:\n"
            "<code>/search KI_25-09</code>",
            parse_mode="HTML"
        )
        await callback.answer()
        
    elif action == "attendance":
        from bot.handlers.attendance import cmd_attendance
        await callback.message.delete()
        
        # Create fake message object with same chat
        class FakeMessage:
            def __init__(self, chat, from_user):
                self.chat = chat
                self.from_user = from_user
                
            async def answer(self, *args, **kwargs):
                return await callback.message.answer(*args, **kwargs)
        
        fake_msg = FakeMessage(callback.message.chat, callback.from_user)
        await cmd_attendance(fake_msg)
        await callback.answer()
        
    elif action == "settings":
        chat_id = callback.message.chat.id
        
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.chat_id == chat_id,
                    Subscription.is_active == True
                )
            )
            subscription = result.scalar_one_or_none()
        
        if subscription:
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
        else:
            text = """
⚙️ <b>Sozlamalar</b>

❌ Bu chat hech qaysi guruhga obuna emas.
"""
            keyboard = get_settings_keyboard(None)
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await callback.answer()
        
    elif action == "help":
        from bot.handlers.start import HELP_MESSAGE
        await callback.message.edit_text(
            HELP_MESSAGE,
            parse_mode="HTML"
        )
        await callback.answer()


@router.callback_query(F.data.startswith("back:"))
async def callback_back(callback: CallbackQuery):
    """Handle back navigation"""
    destination = callback.data.split(":")[1]
    
    if destination == "menu":
        chat_id = callback.message.chat.id
        
        # Check subscription status
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.chat_id == chat_id,
                    Subscription.is_active == True
                )
            )
            subscription = result.scalar_one_or_none()
        
        if subscription:
            text = f"""
🎓 <b>UniControl Bot</b>

✅ <b>{subscription.group_code}</b> guruhiga obuna

<b>Buyruqlar:</b>
📋 /attendance - Bugungi davomat
⚙️ /settings - Sozlamalar
🔍 /search - Boshqa guruh izlash
"""
        else:
            from bot.handlers.start import WELCOME_MESSAGE
            text = WELCOME_MESSAGE
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        
    elif destination == "search":
        await callback.message.edit_text(
            "🔍 <b>Guruh qidirish</b>\n\n"
            "Guruh kodini yoki nomini yozing:\n"
            "<code>/search KI_25-09</code>",
            parse_mode="HTML"
        )
        await callback.answer()
        
    elif destination == "settings":
        # Go to settings
        await callback_menu(callback)


@router.callback_query(F.data == "unsubscribe")
async def callback_unsubscribe_prompt(callback: CallbackQuery):
    """Show unsubscribe confirmation"""
    from bot.keyboards import get_unsubscribe_confirm_keyboard
    
    chat_id = callback.message.chat.id
    
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
    
    await callback.message.edit_text(
        f"⚠️ <b>{subscription.group_code}</b> guruhidan obunani bekor qilishni tasdiqlaysizmi?\n\n"
        f"Endi davomat xabarlari kelmaydi.",
        parse_mode="HTML",
        reply_markup=get_unsubscribe_confirm_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "check_subscription")
async def callback_check_subscription(callback: CallbackQuery):
    """Check if user subscribed to mandatory channels"""
    from aiogram import Bot
    from bot.database import MandatoryChannel
    
    bot: Bot = callback.bot
    user_id = callback.from_user.id
    
    async with async_session() as session:
        result = await session.execute(
            select(MandatoryChannel).where(MandatoryChannel.is_active == True)
        )
        channels = result.scalars().all()
    
    if not channels:
        await callback.answer("✅ Obunalar tekshirildi!", show_alert=True)
        await callback.message.delete()
        return
    
    # Check each channel
    not_subscribed = []
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel.channel_id, user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(channel.channel_title)
        except:
            continue
    
    if not_subscribed:
        await callback.answer(
            f"❌ Hali obuna bo'lmagansiz:\n" + "\n".join(not_subscribed[:3]),
            show_alert=True
        )
    else:
        await callback.answer("✅ Barcha kanallarga obuna bo'lgansiz!", show_alert=True)
        await callback.message.delete()
        # Send welcome message
        await callback.message.answer(
            "✅ Rahmat! Endi botdan foydalanishingiz mumkin.\n\n"
            "Boshlash uchun /start buyrug'ini yuboring.",
            parse_mode="HTML"
        )


@router.callback_query()
async def callback_unknown(callback: CallbackQuery):
    """Handle unknown callbacks"""
    logger.warning(f"Unknown callback: {callback.data}")
    await callback.answer("Noma'lum buyruq")
