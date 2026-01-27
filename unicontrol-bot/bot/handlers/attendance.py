from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select
from datetime import date, timedelta
import logging

from bot.services import UniControlAPI, AttendanceFormatter
from bot.keyboards import get_back_keyboard
from bot.database import async_session, Subscription, UserRegistration

router = Router(name="attendance")
logger = logging.getLogger(__name__)

api = UniControlAPI()


@router.message(Command("attendance"))
async def cmd_attendance(message: Message):
    """
    Handle /attendance command.
    Shows today's attendance for subscribed group.
    """
    chat_id = message.chat.id
    
    # Get subscription
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
            "❌ Bu chat hech qaysi guruhga obuna emas.\n\n"
            "💡 <i>Obuna bo'lish uchun: /subscribe [kod]</i>",
            parse_mode="HTML"
        )
        return
    
    # Show loading
    loading_msg = await message.answer(
        f"📋 <b>{subscription.group_code}</b> davomati yuklanmoqda...",
        parse_mode="HTML"
    )
    
    try:
        # Get today's attendance
        attendances = await api.get_today_attendance(subscription.group_id)
        
        await loading_msg.delete()
        
        # Format and send
        text = AttendanceFormatter.format_group_attendance(
            attendances,
            subscription.group_code,
            date.today().strftime("%d.%m.%Y")
        )
        
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Attendance error: {e}")
        await loading_msg.delete()
        await message.answer(
            "❌ Davomatni yuklashda xatolik yuz berdi.\n"
            "Iltimos, keyinroq qayta urinib ko'ring.",
            parse_mode="HTML"
        )


@router.message(Command("mystatus"))
async def cmd_my_status(message: Message):
    """
    Handle /mystatus command.
    Shows personal attendance for registered users.
    """
    telegram_id = message.from_user.id
    
    # Check registration
    async with async_session() as session:
        result = await session.execute(
            select(UserRegistration).where(
                UserRegistration.telegram_id == telegram_id,
                UserRegistration.is_verified == True
            )
        )
        registration = result.scalar_one_or_none()
    
    if not registration:
        await message.answer(
            "❌ Siz tizimda ro'yxatdan o'tmagansiz.\n\n"
            "💡 <i>Shaxsiy davomatni ko'rish uchun UniControl tizimida "
            "Telegram hisobingizni ulash kerak.</i>",
            parse_mode="HTML"
        )
        return
    
    # Show loading
    loading_msg = await message.answer(
        f"📋 <b>{registration.student_name}</b> davomati yuklanmoqda...",
        parse_mode="HTML"
    )
    
    try:
        # Get this week's attendance
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        attendances = await api.get_student_attendance(
            registration.student_id,
            date_from=week_start,
            date_to=today
        )
        
        await loading_msg.delete()
        
        # Format and send
        text = AttendanceFormatter.format_student_attendance_summary(
            attendances,
            registration.student_name,
            "bu hafta"
        )
        
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"My status error: {e}")
        await loading_msg.delete()
        await message.answer(
            "❌ Davomatni yuklashda xatolik yuz berdi.\n"
            "Iltimos, keyinroq qayta urinib ko'ring.",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("attendance:"))
async def callback_attendance(callback: CallbackQuery):
    """Get attendance for specific group from callback"""
    group_code = callback.data.split(":")[1]
    
    await callback.answer("Yuklanmoqda...")
    
    try:
        # Get group
        group = await api.get_group_by_code(group_code)
        
        if not group:
            await callback.answer("Guruh topilmadi", show_alert=True)
            return
        
        # Get today's attendance
        attendances = await api.get_today_attendance(group.get("id"))
        
        # Format and send
        text = AttendanceFormatter.format_group_attendance(
            attendances,
            group_code,
            date.today().strftime("%d.%m.%Y")
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Attendance callback error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)


@router.callback_query(F.data.startswith("stats:"))
async def callback_stats(callback: CallbackQuery):
    """Get weekly statistics for group"""
    group_code = callback.data.split(":")[1]
    
    await callback.answer("Statistika yuklanmoqda...")
    
    try:
        # Get group
        group = await api.get_group_by_code(group_code)
        
        if not group:
            await callback.answer("Guruh topilmadi", show_alert=True)
            return
        
        # Get this week's attendance
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        attendances = await api.get_group_attendance(
            group.get("id"),
            date_from=week_start,
            date_to=today
        )
        
        # Calculate statistics
        if not attendances:
            await callback.message.edit_text(
                f"📊 <b>Haftalik statistika - {group_code}</b>\n\n"
                f"❌ Bu hafta davomat ma'lumoti yo'q",
                parse_mode="HTML",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Group by status
        stats = {"present": 0, "late": 0, "absent": 0, "excused": 0}
        by_day = {}
        
        for att in attendances:
            status = att.get("status", "unknown")
            if status in stats:
                stats[status] += 1
            
            att_date = att.get("date", "")[:10]
            if att_date not in by_day:
                by_day[att_date] = {"present": 0, "late": 0, "absent": 0, "excused": 0}
            if status in by_day[att_date]:
                by_day[att_date][status] += 1
        
        total = len(attendances)
        present_percent = round((stats["present"] + stats["excused"]) / total * 100) if total > 0 else 0
        
        # Format message
        lines = [
            f"📊 <b>Haftalik statistika - {group_code}</b>",
            f"📅 {week_start.strftime('%d.%m')} - {today.strftime('%d.%m.%Y')}",
            "━" * 22,
            "",
            f"📈 <b>Umumiy davomat: {present_percent}%</b>",
            "",
            f"✅ Keldi: {stats['present']}",
            f"⚠️ Kech qoldi: {stats['late']}",
            f"❌ Kelmadi: {stats['absent']}",
            f"📋 Sababli: {stats['excused']}",
            f"👥 Jami: {total}",
            "",
            "━" * 22,
            "<b>Kunlik:</b>"
        ]
        
        # Day names in Uzbek
        day_names = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
        
        for att_date, day_stats in sorted(by_day.items()):
            try:
                dt = date.fromisoformat(att_date)
                day_name = day_names[dt.weekday()]
                day_total = sum(day_stats.values())
                day_present = day_stats["present"] + day_stats["excused"]
                day_percent = round(day_present / day_total * 100) if day_total > 0 else 0
                lines.append(f"  {day_name} ({att_date[5:10]}): {day_percent}%")
            except:
                continue
        
        await callback.message.edit_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Stats callback error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
