"""
UniControl - Activity Logger Service
=====================================
Utility for logging user activities to the database.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog, ActivityAction
import json
import logging

logger = logging.getLogger(__name__)


async def log_activity(
    db: AsyncSession,
    action: ActivityAction,
    description: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    context: Optional[dict] = None,
):
    """
    Log an activity to the database.
    
    Args:
        db: Database session
        action: ActivityAction enum value
        description: Human-readable description
        user_id: ID of the user performing the action
        entity_type: Type of entity (student, group, user, etc.)
        entity_id: ID of the entity
        old_data: Previous data (for updates)
        new_data: New data (for creates/updates)
        ip_address: Client IP address
        user_agent: Client user agent string
        context: Additional context data
    """
    try:
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=json.dumps(old_data, default=str, ensure_ascii=False) if old_data else None,
            new_data=json.dumps(new_data, default=str, ensure_ascii=False) if new_data else None,
            ip_address=ip_address,
            user_agent=user_agent,
            context=json.dumps(context, default=str, ensure_ascii=False) if context else None,
        )
        db.add(log_entry)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
        # Don't let logging failures break the main flow
        try:
            await db.rollback()
        except:
            pass


def get_client_ip(request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
