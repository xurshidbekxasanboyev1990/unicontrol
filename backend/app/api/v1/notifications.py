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
)
from app.models.notification import NotificationType
from app.core.dependencies import get_current_active_user, require_admin, require_leader
from app.models.user import User

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
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
    
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
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
    notification = await service.create(notification_data)
    return NotificationResponse.model_validate(notification)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def send_bulk_notifications(
    data: NotificationBulkSend,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Send notifications to multiple users.
    
    Requires admin role.
    """
    service = NotificationService(db)
    count = await service.send_bulk_notifications(
        user_ids=data.user_ids,
        title=data.title,
        message=data.message,
        notification_type=data.notification_type
    )
    return {"message": f"Sent {count} notifications"}


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
    
    return NotificationResponse.model_validate(notification)


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
    return NotificationResponse.model_validate(notification)


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
    
    await service.delete(notification_id)
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
