"""
Telegram Bot API Routes
Webhook endpoints for Telegram bot integration
"""
from fastapi import APIRouter, HTTPException, Header, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import httpx
import logging

from app.config import settings
from app.core.dependencies import get_db
from app.models.group import Group
from app.models.attendance import Attendance
from app.models.student import Student
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/telegram", tags=["Telegram Bot"])
logger = logging.getLogger(__name__)


# ==================== Schemas ====================

class TelegramChatRegister(BaseModel):
    """Schema for registering Telegram chat"""
    chat_id: int
    group_code: str
    chat_type: str
    chat_title: Optional[str] = None


class TelegramVerify(BaseModel):
    """Schema for student verification"""
    telegram_id: int
    student_id: int
    verification_code: str


class AttendanceWebhook(BaseModel):
    """Schema for attendance webhook"""
    attendance_id: int
    student_id: int
    student_name: str
    group_code: str
    status: str
    reason: Optional[str] = None
    lesson_number: Optional[int] = None
    date: str


class TelegramNotification(BaseModel):
    """Schema for sending notification to bot"""
    group_code: str
    message: str
    parse_mode: str = "HTML"


# ==================== Bot Token Verification ====================

async def verify_bot_token(x_bot_token: str = Header(None, alias="X-Bot-Token")):
    """Verify request comes from our bot"""
    expected_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if expected_token and x_bot_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid bot token")
    return True


# ==================== Telegram Chat Registry ====================

# In-memory storage for registered chats (in production, use Redis or database)
registered_chats: dict = {}


@router.post("/register")
async def register_telegram_chat(
    data: TelegramChatRegister,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """
    Register a Telegram chat for attendance notifications.
    Called by bot when user subscribes to a group.
    """
    # Verify group exists
    result = await db.execute(
        select(Group).where(Group.name == data.group_code)
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Register chat
    registered_chats[data.chat_id] = {
        "group_code": data.group_code,
        "group_id": group.id,
        "chat_type": data.chat_type,
        "chat_title": data.chat_title,
        "registered_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Registered Telegram chat {data.chat_id} for group {data.group_code}")
    
    return {
        "success": True,
        "message": f"Chat registered for {data.group_code}",
        "group_id": group.id
    }


@router.delete("/unregister/{chat_id}")
async def unregister_telegram_chat(
    chat_id: int,
    _: bool = Depends(verify_bot_token)
):
    """Unregister a Telegram chat from notifications"""
    if chat_id in registered_chats:
        del registered_chats[chat_id]
        logger.info(f"Unregistered Telegram chat {chat_id}")
    
    return {"success": True, "message": "Chat unregistered"}


@router.get("/registered")
async def get_registered_chats(
    group_code: Optional[str] = None,
    _: bool = Depends(verify_bot_token)
):
    """Get list of registered chats"""
    if group_code:
        chats = {
            k: v for k, v in registered_chats.items() 
            if v.get("group_code") == group_code
        }
    else:
        chats = registered_chats
    
    return {"chats": chats, "total": len(chats)}


# ==================== Student Verification ====================

# Verification codes (in production, use Redis with TTL)
verification_codes: dict = {}


@router.post("/verify")
async def verify_student(
    data: TelegramVerify,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """
    Verify student identity for personal attendance access.
    """
    # Check verification code
    stored = verification_codes.get(data.student_id)
    if not stored or stored["code"] != data.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Check if code expired (15 minutes)
    created_at = datetime.fromisoformat(stored["created_at"])
    if (datetime.utcnow() - created_at).seconds > 900:
        del verification_codes[data.student_id]
        raise HTTPException(status_code=400, detail="Verification code expired")
    
    # Get student
    result = await db.execute(
        select(Student).where(Student.id == data.student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Clear used code
    del verification_codes[data.student_id]
    
    logger.info(f"Verified student {data.student_id} for Telegram user {data.telegram_id}")
    
    return {
        "success": True,
        "student_id": student.id,
        "student_name": student.full_name,
        "group_code": student.group.code if student.group else None
    }


@router.post("/generate-code/{student_id}")
async def generate_verification_code(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate verification code for student.
    Called from web app when student wants to link Telegram.
    """
    import random
    import string
    
    # Verify student exists
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Generate 6-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    verification_codes[student_id] = {
        "code": code,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "code": code,
        "expires_in": 900,  # 15 minutes
        "message": "Send this code to the bot to verify your identity"
    }


# ==================== Attendance Webhook ====================

@router.post("/webhook/attendance")
async def attendance_webhook(
    data: AttendanceWebhook,
    background_tasks: BackgroundTasks,
    _: bool = Depends(verify_bot_token)
):
    """
    Webhook endpoint called when attendance is recorded/updated.
    Sends notification to all subscribed Telegram chats.
    """
    # Find all chats subscribed to this group
    target_chats = [
        chat_id for chat_id, info in registered_chats.items()
        if info.get("group_code") == data.group_code
    ]
    
    if not target_chats:
        return {"success": True, "message": "No chats to notify", "notified": 0}
    
    # Queue notification sending
    background_tasks.add_task(
        send_attendance_notifications,
        data,
        target_chats
    )
    
    return {
        "success": True,
        "message": f"Notifications queued for {len(target_chats)} chats",
        "notified": len(target_chats)
    }


async def send_attendance_notifications(
    data: AttendanceWebhook,
    chat_ids: List[int]
):
    """
    Send attendance notifications to Telegram chats.
    Uses bot API directly.
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured")
        return
    
    # Format message
    status_emoji = {
        "present": "✅",
        "late": "⚠️",
        "absent": "❌",
        "excused": "📋"
    }
    status_text = {
        "present": "Keldi",
        "late": "Kech qoldi",
        "absent": "Kelmadi",
        "excused": "Sababli"
    }
    
    emoji = status_emoji.get(data.status, "❓")
    text = status_text.get(data.status, data.status)
    
    message = f"""📋 <b>Davomat yangilandi - {data.group_code}</b>
━━━━━━━━━━━━━━━━━━━━

👤 <b>{data.student_name}</b>
📅 {data.date}""" + (f" | {data.lesson_number}-para" if data.lesson_number else "") + f"""
⏰ Holat: {emoji} <b>{text}</b>"""
    
    if data.reason:
        message += f"\n📝 Sabab: {data.reason}"
    
    message += "\n\n━━━━━━━━━━━━━━━━━━━━"
    
    # Send to all chats
    async with httpx.AsyncClient() as client:
        for chat_id in chat_ids:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=10.0
                )
                logger.info(f"Sent notification to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send to chat {chat_id}: {e}")


# ==================== Group Search ====================

@router.get("/groups/search")
async def search_groups_for_bot(
    q: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """
    Search groups for bot users.
    Returns simplified group info.
    """
    result = await db.execute(
        select(Group).where(
            Group.name.ilike(f"%{q}%") | Group.faculty.ilike(f"%{q}%")
        ).limit(10)
    )
    groups = result.scalars().all()
    
    return {
        "items": [
            {
                "id": g.id,
                "code": g.name,  # Using name as code
                "name": g.name,
                "faculty": g.faculty,
                "course_year": g.course_year,
                "student_count": g.student_count
            }
            for g in groups
        ]
    }


@router.get("/groups/code/{code}")
async def get_group_by_code_for_bot(
    code: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """Get group by exact code"""
    result = await db.execute(
        select(Group).where(Group.name == code.upper())
    )
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return {
        "id": group.id,
        "code": group.name,  # Using name as code
        "name": group.name,
        "faculty": group.faculty,
        "course_year": group.course_year,
        "student_count": group.student_count,
        "leader_name": group.leader.full_name if group.leader else None
    }


# ==================== Attendance Data ====================

@router.get("/attendance/group/{group_id}")
async def get_group_attendance_for_bot(
    group_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """Get attendance records for a group"""
    from datetime import date as date_type
    from sqlalchemy.orm import selectinload
    
    # Get all students in the group first
    student_query = select(Student.id).where(Student.group_id == group_id)
    student_result = await db.execute(student_query)
    student_ids = [s[0] for s in student_result.fetchall()]
    
    if not student_ids:
        return {"items": []}
    
    query = select(Attendance).options(selectinload(Attendance.student)).where(
        Attendance.student_id.in_(student_ids)
    )
    
    if date_from:
        query = query.where(Attendance.date >= date_type.fromisoformat(date_from))
    if date_to:
        query = query.where(Attendance.date <= date_type.fromisoformat(date_to))
    
    result = await db.execute(query.order_by(Attendance.date.desc()))
    records = result.scalars().all()
    
    # Get group info
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    group_code = group.name if group else None
    
    return {
        "items": [
            {
                "id": r.id,
                "student_name": r.student.full_name if r.student else "Unknown",
                "status": r.status.value if r.status else None,
                "reason": r.excuse_reason,
                "lesson_number": r.lesson_number,
                "date": r.date.isoformat() if r.date else None,
                "group_code": group_code
            }
            for r in records
        ]
    }


@router.get("/attendance/group/{group_id}/updates")
async def get_attendance_updates_for_bot(
    group_id: int,
    since: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bot_token)
):
    """Get attendance records updated since a specific time"""
    from sqlalchemy.orm import selectinload
    
    since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
    
    # Get all students in the group
    student_query = select(Student.id).where(Student.group_id == group_id)
    student_result = await db.execute(student_query)
    student_ids = [s[0] for s in student_result.fetchall()]
    
    if not student_ids:
        return {"items": []}
    
    result = await db.execute(
        select(Attendance)
        .options(selectinload(Attendance.student))
        .where(
            Attendance.student_id.in_(student_ids),
            Attendance.updated_at >= since_dt
        )
        .order_by(Attendance.updated_at.desc())
    )
    records = result.scalars().all()
    
    # Get group info
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    group_code = group.name if group else None
    
    return {
        "items": [
            {
                "id": r.id,
                "student_name": r.student.full_name if r.student else "Unknown",
                "status": r.status.value if r.status else None,
                "reason": r.excuse_reason,
                "lesson_number": r.lesson_number,
                "date": r.date.isoformat() if r.date else None,
                "group_code": group_code,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None
            }
            for r in records
        ]
    }
