"""
UniControl - Notification Service
=================================
Handles notification management.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from app.config import now_tashkent
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update

from app.models.notification import (
    Notification,
    BroadcastNotification,
    NotificationType,
    NotificationPriority,
)
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.notification import (
    NotificationCreate,
    BroadcastNotificationCreate,
    NotificationResponse,
)
from app.core.exceptions import NotFoundException


class NotificationService:
    """Notification management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def list_user_notifications(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False
    ) -> Tuple[List[Notification], int, int]:
        """
        List notifications for a user.
        
        Returns:
            Tuple of (notifications, total count, unread count)
        """
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        unread_query = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        # Get counts
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        unread_result = await self.db.execute(unread_query)
        unread = unread_result.scalar()
        
        # Get notifications
        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total, unread

    async def list_notifications(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        is_read: Optional[bool] = None,
        notification_type = None
    ) -> Tuple[List[Notification], int]:
        """
        List notifications for a user (simplified for route).
        """
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
            count_query = count_query.where(Notification.is_read == is_read)
        
        if notification_type is not None:
            query = query.where(Notification.type == notification_type)
            count_query = count_query.where(Notification.type == notification_type)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get notifications
        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        query = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def create(
        self,
        notification_data: NotificationCreate,
        sender_id: Optional[int] = None
    ) -> Notification:
        """Create a notification."""
        notification = Notification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            message=notification_data.message,
            type=notification_data.type,
            priority=notification_data.priority,
            action_url=notification_data.action_url,
            action_text=notification_data.action_text,
            expires_at=notification_data.expires_at,
            sender_id=sender_id,
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> Notification:
        """Mark notification as read."""
        notification = await self.get_by_id(notification_id)
        
        if not notification:
            raise NotFoundException("Notification not found")
        
        if notification.user_id != user_id:
            raise NotFoundException("Notification not found")
        
        notification.is_read = True
        notification.read_at = now_tashkent()
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        result = await self.db.execute(
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True, read_at=now_tashkent())
        )
        
        await self.db.commit()
        return result.rowcount
    
    async def mark_selected_as_read(
        self,
        notification_ids: List[int],
        user_id: int
    ) -> int:
        """Mark selected notifications as read."""
        result = await self.db.execute(
            update(Notification)
            .where(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True, read_at=now_tashkent())
        )
        
        await self.db.commit()
        return result.rowcount
    
    async def delete(self, notification_id: int, user_id: int = None) -> bool:
        """Delete a notification. If user_id provided, check ownership."""
        notification = await self.get_by_id(notification_id)
        
        if not notification:
            raise NotFoundException("Notification not found")
        
        await self.db.delete(notification)
        await self.db.commit()
        
        return True
    
    async def delete_all_read(self, user_id: int) -> int:
        """Delete all read notifications for a user."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == True
                )
            )
        )
        notifications = result.scalars().all()
        
        count = len(notifications)
        for notification in notifications:
            await self.db.delete(notification)
        
        await self.db.commit()
        return count
    
    async def send_bulk(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        notification_type = NotificationType.INFO,
        priority = NotificationPriority.NORMAL,
        sender_id: Optional[int] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
    ) -> int:
        """Send a notification to multiple users."""
        count = 0
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                sender_id=sender_id,
                action_url=action_url,
                action_text=action_text,
            )
            self.db.add(notification)
            count += 1
        
        await self.db.commit()
        return count

    async def create_broadcast(
        self,
        broadcast_data: BroadcastNotificationCreate,
        sender_id: int
    ) -> Tuple[BroadcastNotification, int]:
        """
        Create a broadcast notification.
        
        Returns:
            Tuple of (broadcast, number of notifications sent)
        """
        # Create broadcast record
        broadcast = BroadcastNotification(
            title=broadcast_data.title,
            message=broadcast_data.message,
            type=broadcast_data.type,
            priority=broadcast_data.priority,
            target_role=broadcast_data.target_role,
            target_group_id=broadcast_data.target_group_id,
            action_url=broadcast_data.action_url,
            scheduled_at=broadcast_data.scheduled_at,
            expires_at=broadcast_data.expires_at,
            sender_id=sender_id,
        )
        
        self.db.add(broadcast)
        await self.db.flush()
        
        # Get target users
        target_users = await self._get_broadcast_targets(
            broadcast_data.target_role,
            broadcast_data.target_group_id
        )
        
        # Create individual notifications
        sent_count = 0
        for user_id in target_users:
            notification = Notification(
                user_id=user_id,
                title=broadcast_data.title,
                message=broadcast_data.message,
                type=broadcast_data.type,
                priority=broadcast_data.priority,
                action_url=broadcast_data.action_url,
                expires_at=broadcast_data.expires_at,
                sender_id=sender_id,
            )
            self.db.add(notification)
            sent_count += 1
        
        broadcast.sent_count = sent_count
        broadcast.sent_at = now_tashkent()
        
        await self.db.commit()
        await self.db.refresh(broadcast)
        
        return broadcast, sent_count
    
    async def _get_broadcast_targets(
        self,
        target_role: Optional[str],
        target_group_id: Optional[int]
    ) -> List[int]:
        """Get user IDs for broadcast targets."""
        user_ids = []
        
        if target_group_id:
            # Get students in group
            result = await self.db.execute(
                select(Student.user_id)
                .where(Student.group_id == target_group_id)
                .where(Student.user_id.isnot(None))
            )
            user_ids.extend([row[0] for row in result.all()])
        elif target_role and target_role != "all":
            # Get users by role
            role_map = {
                "student": UserRole.STUDENT,
                "leader": UserRole.LEADER,
                "admin": UserRole.ADMIN,
            }
            role = role_map.get(target_role)
            
            if role:
                result = await self.db.execute(
                    select(User.id)
                    .where(User.role == role)
                    .where(User.is_active == True)
                )
                user_ids.extend([row[0] for row in result.all()])
        else:
            # All active users
            result = await self.db.execute(
                select(User.id).where(User.is_active == True)
            )
            user_ids.extend([row[0] for row in result.all()])
        
        return user_ids
    
    async def send_attendance_notification(
        self,
        student_id: int,
        status: str,
        date: str
    ) -> Optional[Notification]:
        """Send attendance notification to student."""
        # Get student's user
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if not student or not student.user_id:
            return None
        
        if status == "absent":
            title = "Davomat haqida xabar"
            message = f"{date} sanasida darsga kelmadingiz. Iltimos sabab bildiring."
        elif status == "late":
            title = "Kechikish haqida xabar"
            message = f"{date} sanasida darsga kech qoldingiz."
        else:
            return None
        
        notification = Notification(
            user_id=student.user_id,
            title=title,
            message=message,
            type=NotificationType.ATTENDANCE,
            priority=NotificationPriority.NORMAL,
        )
        
        self.db.add(notification)
        await self.db.commit()
        
        return notification
    
    async def send_payment_reminder(
        self,
        student_id: int,
        remaining_amount: float
    ) -> Optional[Notification]:
        """Send payment reminder to student."""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if not student or not student.user_id:
            return None
        
        notification = Notification(
            user_id=student.user_id,
            title="To'lov eslatmasi",
            message=f"Kontrakt to'lovi qoldig'i: {remaining_amount:,.0f} so'm. "
                    "Iltimos o'z vaqtida to'lang.",
            type=NotificationType.PAYMENT,
            priority=NotificationPriority.HIGH,
        )
        
        self.db.add(notification)
        await self.db.commit()
        
        return notification
