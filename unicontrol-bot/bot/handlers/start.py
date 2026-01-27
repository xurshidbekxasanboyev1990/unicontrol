from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from sqlalchemy import select

from bot.database import async_session, Subscription
from bot.keyboards import get_main_menu_keyboard

router = Router(name="start")


WELCOME_MESSAGE = """
🎓 <b>UniControl Bot</b>ga xush kelibsiz!

Bu bot orqali siz guruhingiz davomatini kuzatishingiz mumkin.

<b>Asosiy funksiyalar:</b>
• 🔍 Guruh izlash va obuna bo'lish
• 📋 Kunlik davomat hisoboti
• ⚠️ Kech qolish/kelmaslik xabarlari
• 📊 Haftalik statistika

<b>Buyruqlar:</b>
/search [kod] - Guruh izlash
/subscribe [kod] - Obuna bo'lish
/attendance - Bugungi davomat
/unsubscribe - Obunani bekor qilish
/help - Yordam

💡 <i>Boshlash uchun guruhingizni qidiring!</i>
"""


HELP_MESSAGE = """
❓ <b>Yordam</b>

<b>Bot qanday ishlaydi:</b>
1. /search buyrug'i bilan guruhingizni toping
2. /subscribe buyrug'i bilan obuna bo'ling
3. Davomat yangiliklari avtomatik keladi

<b>Buyruqlar ro'yxati:</b>

🔍 <code>/search KI_25-09</code>
Guruh kodi yoki nomi bo'yicha qidirish

✅ <code>/subscribe KI_25-09</code>
Guruhga obuna bo'lish (davomat xabarlari keladi)

📋 <code>/attendance</code>
Bugungi davomat hisoboti

🚫 <code>/unsubscribe</code>
Obunani bekor qilish

⚙️ <code>/settings</code>
Xabar sozlamalari

<b>Guruhda ishlatish:</b>
Botni guruhga qo'shing va /subscribe buyrug'ini yuboring.
Davomat yangiliklari shu guruhga keladi.

<b>Muammo bo'lsa:</b>
Guruh sardoringiz yoki admin bilan bog'laning.
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    chat_type = message.chat.type
    chat_id = message.chat.id
    
    # Check if already subscribed
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

✅ Bu chat <b>{subscription.group_code}</b> guruhiga obuna.

📋 Bugungi davomatni ko'rish: /attendance
⚙️ Sozlamalar: /settings
"""
    else:
        text = WELCOME_MESSAGE
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.answer(
        HELP_MESSAGE,
        parse_mode="HTML"
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command"""
    from bot.keyboards import get_settings_keyboard
    
    chat_id = message.chat.id
    
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

Obuna bo'lish uchun:
1. /search buyrug'i bilan guruh toping
2. /subscribe buyrug'i bilan obuna bo'ling
"""
        keyboard = get_settings_keyboard(None)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
