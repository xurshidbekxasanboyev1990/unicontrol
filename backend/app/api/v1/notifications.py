"""
UniControl - Notification Routes
================================
Notification management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationBulkSend,
    BroadcastNotificationCreate,
)
from app.models.notification import NotificationType
from app.core.dependencies import get_current_active_user, require_admin, require_leader
from app.models.user import User

router = APIRouter()


def _notification_to_response(n) -> dict:
    """Convert Notification model to response dict with sender_name."""
    data = {
        "id": n.id,
        "user_id": n.user_id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "priority": n.priority,
        "is_read": n.is_read,
        "read_at": n.read_at,
        "action_url": n.action_url,
        "action_text": n.action_text,
        "sender_id": n.sender_id,
        "sender_name": n.sender.name if n.sender else None,
        "data": n.data,
        "push_sent": n.push_sent,
        "email_sent": n.email_sent,
        "expires_at": n.expires_at,
        "created_at": n.created_at,
    }
    return data


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List current user's notifications.
    """
    service = NotificationService(db)
    notifications, total = await service.list_notifications(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_read=is_read,
        notification_type=notification_type
    )
    
    # Get unread count
    unread_count = await service.get_unread_count(current_user.id)
    
    return NotificationListResponse(
        items=[NotificationResponse(**_notification_to_response(n)) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create a notification for a user.
    
    Requires leader role or higher.
    """
    service = NotificationService(db)
    notification = await service.create(notification_data, sender_id=current_user.id)
    return NotificationResponse(**_notification_to_response(notification))


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def send_bulk_notifications(
    data: NotificationBulkSend,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Send notifications to multiple users.
    
    Requires leader role or higher.
    """
    service = NotificationService(db)
    count = await service.send_bulk(
        user_ids=data.user_ids,
        title=data.title,
        message=data.message,
        notification_type=data.type,
        priority=data.priority,
        sender_id=current_user.id,
        action_url=data.action_url,
        action_text=data.action_text,
    )
    return {"message": f"Sent {count} notifications", "count": count}


@router.post("/broadcast", status_code=status.HTTP_201_CREATED)
async def broadcast_notification(
    data: BroadcastNotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Broadcast notification to users by role or group.
    
    Requires leader role or higher.
    """
    service = NotificationService(db)
    broadcast, count = await service.create_broadcast(data, sender_id=current_user.id)
    return {
        "message": f"Sent {count} notifications",
        "count": count,
        "broadcast_id": broadcast.id
    }


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get unread notifications count.
    """
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return {"count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get notification by ID.
    """
    service = NotificationService(db)
    notification = await service.get_by_id(notification_id)
    
    if not notification:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Notification not found")
    
    # Check ownership
    if notification.user_id != current_user.id and current_user.role.value not in ["admin", "superadmin"]:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Not allowed to access this notification")
    
    return NotificationResponse(**_notification_to_response(notification))


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark notification as read.
    """
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    return NotificationResponse(**_notification_to_response(notification))


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read_put(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark notification as read (PUT alias for mobile compatibility).
    """
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    return NotificationResponse(**_notification_to_response(notification))


@router.post("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark all notifications as read.
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.put("/read-all")
async def mark_all_as_read_put(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark all notifications as read (PUT alias for mobile compatibility).
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete notification.
    """
    service = NotificationService(db)
    notification = await service.get_by_id(notification_id)
    
    if not notification:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Notification not found")
    
    # Check ownership
    if notification.user_id != current_user.id and current_user.role.value not in ["admin", "superadmin"]:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Not allowed to delete this notification")
    
    await service.delete(notification_id, current_user.id)
    return {"message": "Notification deleted"}


@router.delete("")
async def delete_all_read_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete all read notifications.
    """
    service = NotificationService(db)
    count = await service.delete_all_read(current_user.id)
    return {"message": f"Deleted {count} notifications"}
