"""
UniControl - Notification Schemas
=================================
Pydantic schemas for notification-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.notification import NotificationType, NotificationPriority


class NotificationBase(BaseModel):
    """Base notification schema."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schema for creating notification."""
    user_id: int


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    is_read: bool
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    data: Optional[str] = None
    push_sent: bool
    email_sent: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema for notification list."""
    items: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class MarkAsRead(BaseModel):
    """Schema for marking notifications as read."""
    notification_ids: List[int]


class BroadcastNotificationCreate(BaseModel):
    """Schema for creating broadcast notification."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: NotificationType = NotificationType.ANNOUNCEMENT
    priority: NotificationPriority = NotificationPriority.NORMAL
    target_role: Optional[str] = None  # student, leader, admin, all
    target_group_id: Optional[int] = None
    action_url: Optional[str] = Field(None, max_length=500)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class BroadcastNotificationResponse(BaseModel):
    """Schema for broadcast notification response."""
    id: int
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    target_role: Optional[str] = None
    target_group_id: Optional[int] = None
    sender_id: int
    sender_name: Optional[str] = None
    action_url: Optional[str] = None
    is_active: bool
    sent_count: int
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PushSubscription(BaseModel):
    """Schema for push notification subscription."""
    device_token: str
    device_type: str = Field(..., pattern="^(ios|android|web)$")
    device_name: Optional[str] = None
