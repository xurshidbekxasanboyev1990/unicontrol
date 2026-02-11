import asyncio
import logging
from datetime import datetime, timedelta
from bot.config import now_tashkent
from typing import Dict, List, Optional
from sqlalchemy import select
from aiogram import Bot

from bot.config import settings
from bot.database import async_session, Subscription, SentNotification
from bot.services import UniControlAPI, AttendanceFormatter

logger = logging.getLogger(__name__)


class AttendanceNotifier:
    """
    Background service that checks for attendance updates
    and sends notifications to subscribed Telegram chats.
    """
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api = UniControlAPI()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.last_check: Dict[int, datetime] = {}  # group_id -> last check time
    
    async def start(self):
        """Start the notifier background task"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Attendance notifier started")
    
    async def stop(self):
        """Stop the notifier"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.api.close()
        logger.info("Attendance notifier stopped")
    
    async def _run_loop(self):
        """Main loop that checks for updates periodically"""
        while self.running:
            try:
                await self._check_all_subscriptions()
            except Exception as e:
                logger.error(f"Error in notifier loop: {e}")
            
            # Wait before next check
            await asyncio.sleep(settings.attendance_check_interval)
    
    async def _check_all_subscriptions(self):
        """Check all active subscriptions for updates"""
        # Get all active subscriptions grouped by academic group
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(Subscription.is_active == True)
            )
            subscriptions = result.scalars().all()
        
        if not subscriptions:
            return
        
        # Group subscriptions by academic group
        group_subs: Dict[int, List[Subscription]] = {}
        for sub in subscriptions:
            if sub.group_id:
                if sub.group_id not in group_subs:
                    group_subs[sub.group_id] = []
                group_subs[sub.group_id].append(sub)
        
        # Check each group for updates
        for group_id, subs in group_subs.items():
            try:
                await self._check_group_updates(group_id, subs)
            except Exception as e:
                logger.error(f"Error checking group {group_id}: {e}")
    
    async def _check_group_updates(
        self, 
        group_id: int, 
        subscriptions: List[Subscription]
    ):
        """Check a specific group for attendance updates"""
        # Get last check time for this group
        last_check = self.last_check.get(group_id, now_tashkent() - timedelta(minutes=10))
        
        # Get recent updates from API
        updates = await self.api.get_recent_attendance_updates(group_id, last_check)
        
        if not updates:
            self.last_check[group_id] = now_tashkent()
            return
        
        # Process each update
        for attendance in updates:
            await self._notify_subscriptions(attendance, subscriptions)
        
        self.last_check[group_id] = now_tashkent()
    
    async def _notify_subscriptions(
        self, 
        attendance: Dict, 
        subscriptions: List[Subscription]
    ):
        """Send attendance notification to all relevant subscriptions"""
        attendance_id = attendance.get("id")
        status = attendance.get("status", "")
        
        for sub in subscriptions:
            try:
                # Check if should notify based on settings
                if not self._should_notify(sub, status):
                    continue
                
                # Check if already sent
                if await self._is_already_sent(sub.chat_id, attendance_id):
                    continue
                
                # Format and send message
                message_text = AttendanceFormatter.format_attendance_update(
                    attendance,
                    sub.group_code
                )
                
                sent_message = await self.bot.send_message(
                    chat_id=sub.chat_id,
                    text=message_text,
                    parse_mode="HTML"
                )
                
                # Record sent notification
                await self._record_sent(
                    sub.chat_id, 
                    attendance_id, 
                    attendance.get("student_name"),
                    status,
                    sent_message.message_id
                )
                
                logger.info(
                    f"Sent notification to {sub.chat_id} for attendance {attendance_id}"
                )
                
            except Exception as e:
                logger.error(f"Error sending to {sub.chat_id}: {e}")
    
    def _should_notify(self, subscription: Subscription, status: str) -> bool:
        """Check if should send notification based on subscription settings"""
        if status == "present" and not subscription.notify_present:
            return False
        if status == "late" and not subscription.notify_late:
            return False
        if status == "absent" and not subscription.notify_absent:
            return False
        return True
    
    async def _is_already_sent(self, chat_id: int, attendance_id: int) -> bool:
        """Check if notification was already sent"""
        async with async_session() as session:
            result = await session.execute(
                select(SentNotification).where(
                    SentNotification.chat_id == chat_id,
                    SentNotification.attendance_id == attendance_id
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def _record_sent(
        self,
        chat_id: int,
        attendance_id: int,
        student_name: str,
        status: str,
        message_id: int
    ):
        """Record that notification was sent"""
        async with async_session() as session:
            notification = SentNotification(
                chat_id=chat_id,
                attendance_id=attendance_id,
                student_name=student_name,
                status=status,
                message_id=message_id
            )
            session.add(notification)
            await session.commit()
    
    async def send_immediate_notification(
        self,
        group_code: str,
        attendance: Dict
    ):
        """
        Send immediate notification for a new attendance record.
        Called by webhook from backend.
        """
        # Get all subscriptions for this group
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.group_code == group_code,
                    Subscription.is_active == True
                )
            )
            subscriptions = result.scalars().all()
        
        if not subscriptions:
            return
        
        await self._notify_subscriptions(attendance, subscriptions)
