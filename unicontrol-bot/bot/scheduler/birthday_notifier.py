"""
Birthday Notifier - Sends birthday congratulations at 6:00 AM Tashkent time.
Sends to:
1. Student's group chat (if connected to bot)
2. Student's personal chat (if registered with bot)
3. Creates notification in UniControl system
"""
import asyncio
import logging
from datetime import datetime, time as dtime
from typing import Optional, List, Dict

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from bot.config import settings, now_tashkent, today_tashkent, TASHKENT_TZ
from bot.database import async_session, Subscription, UserRegistration

logger = logging.getLogger(__name__)

# Birthday message template
BIRTHDAY_MESSAGE = """🎉 <b>Bugun sizning kuningiz, hurmatli {name}!</b>

Tug'ilgan kuningiz muborak bo'lsin! O'qishlaringizda yuqori natijalar, hayotingizda katta imkoniyatlar va atrofingizda doimo yaxshi insonlar bo'lishini tilaymiz. Har bir yil sizni yanada kuchliroq, bilimliroq va yanada muvaffaqiyatli inson bo'lishingizga xizmat qilsin.

🎓 <b>KUAF va Unicontrol jamoasi</b> sizga yorqin kelajak va yangi marralarni zabt etishda ulkan zafarlar tilaydi!

<b>Yangi yoshingiz muborak bo'lsin!</b> 🎂✨

🎈 <i>{age} yoshga to'ldingiz!</i>"""

# Group message (slightly different)
GROUP_BIRTHDAY_MESSAGE = """🎉🎂 <b>Tug'ilgan kun tabrigi!</b>

Bugun <b>{name}</b>ning tug'ilgan kuni!

Tug'ilgan kuningiz muborak bo'lsin! O'qishlaringizda yuqori natijalar, hayotingizda katta imkoniyatlar va atrofingizda doimo yaxshi insonlar bo'lishini tilaymiz. Har bir yil sizni yanada kuchliroq, bilimliroq va yanada muvaffaqiyatli inson bo'lishingizga xizmat qilsin.

🎓 <b>KUAF va Unicontrol jamoasi</b> sizga yorqin kelajak va yangi marralarni zabt etishda ulkan zafarlar tilaydi!

<b>Yangi yoshingiz muborak bo'lsin!</b> 🎂✨

🎈 <i>{age} yoshga to'ldi!</i>"""


class BirthdayNotifier:
    """
    Background service that sends birthday congratulations
    every day at 6:00 AM Tashkent time.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._sent_today: set = set()  # Track sent student IDs for today
        self._last_date = None

    async def start(self):
        """Start the birthday notifier background task"""
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🎂 Birthday notifier started")

    async def stop(self):
        """Stop the notifier"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🎂 Birthday notifier stopped")

    async def _run_loop(self):
        """Main loop - checks every minute if it's time to send"""
        while self.running:
            try:
                now = now_tashkent()
                today = now.date()

                # Reset sent tracking on new day
                if self._last_date != today:
                    self._sent_today.clear()
                    self._last_date = today

                # Send at 6:00 AM Tashkent time (or later if bot just started)
                if now.hour >= 6 and not self._sent_today:
                    await self._send_birthday_greetings()

            except Exception as e:
                logger.error(f"Birthday notifier error: {e}", exc_info=True)

            # Check every 60 seconds
            await asyncio.sleep(60)

    async def _send_birthday_greetings(self):
        """Fetch birthdays from API and send messages"""
        import aiohttp

        base_url = settings.api_base_url.rstrip("/")
        url = f"{base_url}/telegram/birthdays/today"

        try:
            async with aiohttp.ClientSession(
                headers={
                    "X-Bot-Token": settings.bot_token,
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        error = await response.text()
                        logger.error(f"Birthday API error {response.status}: {error}")
                        return
                    data = await response.json()

            birthdays = data.get("birthdays", [])
            if not birthdays:
                logger.info("🎂 No birthdays today")
                self._sent_today.add("checked")
                return

            logger.info(f"🎂 Found {len(birthdays)} birthday(s) today!")

            for student in birthdays:
                student_id = student.get("student_id")
                if student_id in self._sent_today:
                    continue

                await self._send_to_student(student)
                self._sent_today.add(student_id)

                # Small delay between messages
                await asyncio.sleep(0.5)

            self._sent_today.add("checked")
            logger.info(f"🎂 Birthday greetings sent to {len(birthdays)} student(s)")

        except Exception as e:
            logger.error(f"Birthday API request error: {e}", exc_info=True)

    async def _send_to_student(self, student: Dict):
        """Send birthday message to a student (group + personal)"""
        name = student.get("name", "Talaba")
        age = student.get("age", 0)
        group_code = student.get("group_code")
        group_id = student.get("group_id")
        user_id = student.get("user_id")

        # 1. Send to group chat (if connected)
        if group_code:
            await self._send_to_group_chat(group_code, name, age)

        # 2. Send to personal chat (if registered with bot)
        await self._send_to_personal_chat(student, name, age)

        # 3. Create system notification
        await self._create_system_notification(student, name, age)

    async def _send_to_group_chat(self, group_code: str, name: str, age: int):
        """Send birthday message to connected GROUP chats only (not private)"""
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.group_code == group_code,
                    Subscription.is_active == True,
                    Subscription.chat_type.in_(["group", "supergroup"])
                )
            )
            subscriptions = result.scalars().all()

        for sub in subscriptions:
            try:
                message = GROUP_BIRTHDAY_MESSAGE.format(name=name, age=age)
                await self.bot.send_message(
                    chat_id=sub.chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                logger.info(f"🎂 Birthday sent to group chat {sub.chat_id} ({sub.group_code}) for {name}")
            except Exception as e:
                logger.error(f"Failed to send birthday to chat {sub.chat_id}: {e}")

    async def _send_to_personal_chat(self, student: Dict, name: str, age: int):
        """Send personal birthday message if student registered with bot"""
        student_id = student.get("student_id")

        async with async_session() as session:
            # Find by student_id in registrations
            result = await session.execute(
                select(UserRegistration).where(
                    UserRegistration.student_id == student_id,
                    UserRegistration.is_verified == True
                )
            )
            registration = result.scalar_one_or_none()

        if registration:
            try:
                message = BIRTHDAY_MESSAGE.format(name=name, age=age)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🎓 UniControl platformasiga o'tish",
                        url="https://unicontrol.uz"
                    )]
                ])
                await self.bot.send_message(
                    chat_id=registration.telegram_id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logger.info(f"🎂 Personal birthday sent to {registration.telegram_id} for {name}")
            except Exception as e:
                logger.error(f"Failed to send personal birthday to {registration.telegram_id}: {e}")

    async def _create_system_notification(self, student: Dict, name: str, age: int):
        """Create notification in UniControl system"""
        import aiohttp

        user_id = student.get("user_id")
        if not user_id:
            return

        base_url = settings.api_base_url.rstrip("/")
        url = f"{base_url}/telegram/birthdays/notify"

        try:
            payload = {
                "user_id": user_id,
                "student_name": name,
                "age": age
            }
            async with aiohttp.ClientSession(
                headers={
                    "X-Bot-Token": settings.bot_token,
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=15)
            ) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"🎂 System notification created for {name}")
                    else:
                        error = await response.text()
                        logger.warning(f"System notification error for {name}: {error}")
        except Exception as e:
            logger.warning(f"System notification request error for {name}: {e}")

    async def send_now(self):
        """Force send birthday greetings now (for testing)"""
        logger.info("🎂 Force sending birthday greetings...")
        self._sent_today.clear()
        await self._send_birthday_greetings()
