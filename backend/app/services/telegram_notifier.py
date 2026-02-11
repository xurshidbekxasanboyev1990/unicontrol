"""
UniControl - Telegram Notifier Service
=======================================
Sends real-time attendance notifications to Telegram groups and private chats.
Uses Telegram Bot API directly when attendance is created/updated.

Author: UniControl Team
Version: 1.0.0
"""

import httpx
import logging
from typing import Optional, List, Dict
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import settings, now_tashkent, today_tashkent
from app.models.group import Group
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.subscription import GroupSubscription, SubscriptionStatus, SubscriptionSettings

logger = logging.getLogger(__name__)


async def _mark_attendance_notified(attendance_ids: List[int]):
    """Mark attendance records as notified via Telegram (using own session)."""
    from app.database import async_session_maker
    try:
        async with async_session_maker() as db:
            await db.execute(
                update(Attendance)
                .where(Attendance.id.in_(attendance_ids))
                .values(telegram_notified=True)
            )
            await db.commit()
            logger.debug(f"Marked {len(attendance_ids)} attendance records as telegram_notified")
    except Exception as e:
        logger.error(f"Error marking attendance as notified: {e}")

# In-memory registry of Telegram chats (synced with telegram.py)
_registered_chats: Optional[dict] = None


def get_registered_chats():
    """Get registered chats from telegram router"""
    global _registered_chats
    if _registered_chats is None:
        try:
            from app.api.v1.telegram import registered_chats
            _registered_chats = registered_chats
        except ImportError:
            _registered_chats = {}
    return _registered_chats


# Status display mappings
STATUS_EMOJI = {
    "present": "✅",
    "late": "⚠️",
    "absent": "❌",
    "excused": "📋"
}

STATUS_TEXT = {
    "present": "Keldi",
    "late": "Kech qoldi",
    "absent": "Kelmadi",
    "excused": "Sababli"
}


async def check_group_has_bot_subscription_standalone(group_id: int) -> bool:
    """Check if group has active subscription that includes bot access (Plus+).
    Creates its own DB session to avoid issues with background tasks."""
    from app.database import async_session_maker
    
    BOT_ALLOWED_PLANS = ["plus", "pro", "unlimited"]
    today = today_tashkent()

    try:
        async with async_session_maker() as db:
            result = await db.execute(
                select(GroupSubscription)
                .where(
                    GroupSubscription.group_id == group_id,
                    GroupSubscription.status.in_([
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.TRIAL.value
                    ])
                )
                .order_by(GroupSubscription.end_date.desc())
                .limit(1)
            )
            sub = result.scalar_one_or_none()

            if sub and today <= sub.end_date and sub.plan_type in BOT_ALLOWED_PLANS:
                return True

            # Check trial period
            settings_result = await db.execute(select(SubscriptionSettings).limit(1))
            settings_obj = settings_result.scalar_one_or_none()
            if settings_obj and settings_obj.trial_end_date and today <= settings_obj.trial_end_date:
                return True
    except Exception as e:
        logger.error(f"Error checking subscription for group {group_id}: {e}")

    return False


async def send_attendance_to_telegram(
    db: AsyncSession,
    attendance,
    student,
    group
):
    """
    Send a single attendance notification to all registered Telegram chats for this group.
    Called immediately when leader marks attendance.
    Note: attendance/student/group are passed as objects but we extract values immediately
    since the db session may be closed in background tasks.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        logger.debug("TELEGRAM_BOT_TOKEN not configured, skipping Telegram notification")
        return

    # Extract values immediately (before db session closes)
    try:
        att_id = attendance.id
        group_code = group.name
        group_id = group.id
        student_name = getattr(student, 'full_name', None) or getattr(student, 'name', 'Noma\'lum')
        student_id_str = getattr(student, 'student_id', '') or getattr(student, 'hemis_id', '') or ''
        status_val = attendance.status.value if hasattr(attendance.status, 'value') else str(attendance.status)
        att_date = attendance.date.strftime("%d.%m.%Y") if attendance.date else now_tashkent().strftime("%d.%m.%Y")
        lesson_number = attendance.lesson_number
        subject = attendance.subject
        late_minutes = attendance.late_minutes
        note = attendance.note
        excuse_reason = attendance.excuse_reason
    except Exception as e:
        logger.error(f"Error extracting attendance data: {e}")
        return

    # Check if group has bot subscription (uses its own session)
    has_sub = await check_group_has_bot_subscription_standalone(group_id)
    if not has_sub:
        logger.debug(f"Group {group_code} has no bot subscription, skipping")
        return

    # Find all registered chats for this group
    chats = get_registered_chats()
    target_chats = [
        chat_id for chat_id, info in chats.items()
        if info.get("group_id") == group_id or info.get("group_code") == group_code
    ]

    if not target_chats:
        logger.debug(f"No Telegram chats registered for group {group_code}")
        return

    # Format message
    emoji = STATUS_EMOJI.get(status_val, "❓")
    text = STATUS_TEXT.get(status_val, status_val)

    message = f"""📋 <b>Davomat — {group_code}</b>
━━━━━━━━━━━━━━━━━━━━

👤 <b>{student_name}</b>"""

    if student_id_str:
        message += f"\n🆔 {student_id_str}"

    message += f"\n📅 {att_date}"

    if lesson_number:
        message += f" | {lesson_number}-para"

    if subject:
        message += f"\n📚 {subject}"

    message += f"\n⏰ Holat: {emoji} <b>{text}</b>"

    if late_minutes and late_minutes > 0:
        message += f" ({late_minutes} daqiqa)"

    if note:
        message += f"\n📝 Izoh: {note}"

    if excuse_reason:
        message += f"\n📋 Sabab: {excuse_reason}"

    now = now_tashkent()
    message += f"\n\n🕐 {now.strftime('%H:%M:%S')}"
    message += "\n━━━━━━━━━━━━━━━━━━━━"

    # Send to all chats
    async with httpx.AsyncClient() as client:
        for chat_id in target_chats:
            try:
                resp = await client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=10.0
                )
                if resp.status_code == 200:
                    logger.info(f"Sent attendance notification to chat {chat_id} for {student_name}")
                else:
                    logger.warning(f"Telegram API error for chat {chat_id}: {resp.status_code} - {resp.text}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification to chat {chat_id}: {e}")

    # Mark as notified so bot's polling notifier doesn't re-send
    await _mark_attendance_notified([att_id])


async def send_batch_attendance_summary_to_telegram(
    db: AsyncSession,
    attendances: list,
    group,
    lesson_number: int = None,
    subject: str = None,
    is_update: bool = False,
):
    """
    Send ONE summary message for a batch of attendance records.
    Instead of 50 individual messages, sends a single group summary.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return

    try:
        group_code = group.name
        group_id = group.id
    except Exception as e:
        logger.error(f"Error extracting group data: {e}")
        return

    # Check subscription
    has_sub = await check_group_has_bot_subscription_standalone(group_id)
    if not has_sub:
        logger.debug(f"Group {group_code} has no bot subscription, skipping batch summary")
        return

    # Find all registered chats for this group
    chats = get_registered_chats()
    target_chats = [
        chat_id for chat_id, info in chats.items()
        if info.get("group_id") == group_id or info.get("group_code") == group_code
    ]

    if not target_chats:
        logger.debug(f"No Telegram chats registered for group {group_code}")
        return

    # Extract attendance data safely
    try:
        records = []
        for att in attendances:
            status_val = att.status.value if hasattr(att.status, 'value') else str(att.status)
            student_name = "Noma'lum"
            if hasattr(att, 'student') and att.student:
                student_name = getattr(att.student, 'full_name', None) or getattr(att.student, 'name', "Noma'lum")
            elif hasattr(att, '_student_name'):
                student_name = att._student_name
            records.append({
                "name": student_name,
                "status": status_val,
                "late_minutes": att.late_minutes or 0,
                "note": att.note or "",
                "excuse_reason": att.excuse_reason or "",
            })
    except Exception as e:
        logger.error(f"Error extracting batch attendance data: {e}")
        return

    # Count stats
    total = len(records)
    present = sum(1 for r in records if r["status"] == "present")
    absent = sum(1 for r in records if r["status"] == "absent")
    late = sum(1 for r in records if r["status"] == "late")
    excused = sum(1 for r in records if r["status"] == "excused")

    today_str = now_tashkent().strftime("%d.%m.%Y")
    action = "📝 Tahrirlandi" if is_update else "📋 Davomat"

    message = f"""{action} — <b>{group_code}</b>
━━━━━━━━━━━━━━━━━━━━
📅 {today_str}"""

    if lesson_number:
        message += f" | {lesson_number}-para"
    if subject:
        message += f"\n📚 {subject}"

    message += f"""

👥 Jami: <b>{total}</b> ta talaba
✅ Keldi: <b>{present}</b>
❌ Kelmadi: <b>{absent}</b>
⚠️ Kech qoldi: <b>{late}</b>
📋 Sababli: <b>{excused}</b>"""

    # List absent students
    absent_list = [r for r in records if r["status"] == "absent"]
    if absent_list:
        message += "\n\n❌ <b>Kelmaganlar:</b>"
        for i, r in enumerate(absent_list, 1):
            message += f"\n  {i}. {r['name']}"
            if r.get("excuse_reason"):
                message += f" — {r['excuse_reason']}"

    # List late students
    late_list = [r for r in records if r["status"] == "late"]
    if late_list:
        message += "\n\n⚠️ <b>Kech qolganlar:</b>"
        for i, r in enumerate(late_list, 1):
            mins = r.get("late_minutes", 0)
            message += f"\n  {i}. {r['name']}"
            if mins and mins > 0:
                message += f" ({mins} daq)"
            if r.get("note"):
                message += f" — {r['note']}"

    # List excused students
    excused_list = [r for r in records if r["status"] == "excused"]
    if excused_list:
        message += "\n\n📋 <b>Sabablilar:</b>"
        for i, r in enumerate(excused_list, 1):
            message += f"\n  {i}. {r['name']}"
            if r.get("excuse_reason"):
                message += f" — {r['excuse_reason']}"

    now = now_tashkent()
    message += f"\n\n🕐 {now.strftime('%H:%M:%S')}"
    message += "\n━━━━━━━━━━━━━━━━━━━━"

    # Send to all chats — ONE message
    async with httpx.AsyncClient() as client:
        for chat_id in target_chats:
            try:
                resp = await client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=15.0
                )
                if resp.status_code == 200:
                    logger.info(f"Sent batch attendance summary to chat {chat_id} for {group_code} ({total} students)")
                else:
                    logger.warning(f"Telegram API error for chat {chat_id}: {resp.status_code} - {resp.text}")
            except Exception as e:
                logger.error(f"Failed to send batch summary to chat {chat_id}: {e}")

    # Mark all attendance records as notified so bot's polling notifier doesn't re-send
    try:
        att_ids = [att.id for att in attendances if hasattr(att, 'id') and att.id]
        if att_ids:
            await _mark_attendance_notified(att_ids)
    except Exception as e:
        logger.error(f"Error marking batch as notified: {e}")