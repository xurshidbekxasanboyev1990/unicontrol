"""
UniControl - Notification Model
===============================
Notification model for system notifications.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, Enum):
    """Notification type enum."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ATTENDANCE = "attendance"
    PAYMENT = "payment"
    SCHEDULE = "schedule"
    ANNOUNCEMENT = "announcement"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    """Notification priority enum."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Notification model.
    
    Manages system notifications for users.
    """
    
    __tablename__ = "notifications"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Recipient
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Recipient user ID"
    )
    
    # Title and message
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Notification title"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Notification message"
    )
    
    # Type and priority
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType),
        nullable=False,
        default=NotificationType.INFO,
        comment="Notification type"
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        SAEnum(NotificationPriority),
        nullable=False,
        default=NotificationPriority.NORMAL,
        comment="Notification priority"
    )
    
    # Read status
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Read status"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when notification was read"
    )
    
    # Action link
    action_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Action URL when notification is clicked"
    )
    action_text: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Action button text"
    )
    
    # Sender
    sender_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Sender user ID"
    )
    
    # Additional data
    data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional data as JSON"
    )
    
    # Push notification
    push_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Push notification sent"
    )
    push_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when push was sent"
    )
    
    # Email notification
    email_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email notification sent"
    )
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when email was sent"
    )
    
    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Expiry time"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )
    
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.now(TASHKENT_TZ)
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(TASHKENT_TZ) > self.expires_at
    
    @property
    def is_urgent(self) -> bool:
        """Check if notification is urgent."""
        return self.priority == NotificationPriority.URGENT


class BroadcastNotification(Base):
    """
    Broadcast notification model.
    
    For sending notifications to multiple users at once.
    """
    
    __tablename__ = "broadcast_notifications"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Title and message
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Notification title"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Notification message"
    )
    
    # Type and priority
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType),
        nullable=False,
        default=NotificationType.ANNOUNCEMENT,
        comment="Notification type"
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        SAEnum(NotificationPriority),
        nullable=False,
        default=NotificationPriority.NORMAL,
        comment="Notification priority"
    )
    
    # Target audience
    target_role: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Target role (student, leader, admin, all)"
    )
    target_group_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
        comment="Target group ID"
    )
    
    # Sender
    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="Sender user ID"
    )
    
    # Action link
    action_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Action URL"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Active status"
    )
    sent_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of notifications sent"
    )
    
    # Schedule
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled send time"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual send time"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Expiry time"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    
    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        return f"<BroadcastNotification(id={self.id}, title='{self.title}')>"
