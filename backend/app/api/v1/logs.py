"""
Logs API Routes (SuperAdmin only)
Uses ActivityLog database model for real activity tracking.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, and_
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.activity_log import ActivityLog, ActivityAction
from app.core.dependencies import get_current_active_user

router = APIRouter()


class LogEntryResponse(BaseModel):
    """Log entry response model"""
    id: int
    created_at: datetime
    action: str
    description: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    context: Optional[str] = None

    class Config:
        from_attributes = True


class LogsResponse(BaseModel):
    """Logs list response"""
    items: List[LogEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LogStatsResponse(BaseModel):
    """Log statistics"""
    total: int
    auth_count: int
    crud_count: int
    system_count: int
    error_count: int
    today_count: int


def _get_action_category(action: str) -> str:
    """Get category for an action."""
    auth_actions = ['login', 'logout', 'login_failed', 'password_change', 'password_reset']
    crud_actions = ['create', 'read', 'update', 'delete', 'import', 'export']
    error_actions = ['error']
    
    if action in auth_actions:
        return 'auth'
    elif action in crud_actions:
        return 'crud'
    elif action in error_actions:
        return 'error'
    else:
        return 'system'


@router.get("/stats", response_model=LogStatsResponse)
async def get_log_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get log statistics."""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin")
    
    # Total count
    total_result = await db.execute(select(func.count(ActivityLog.id)))
    total = total_result.scalar() or 0
    
    # Auth actions count
    auth_actions = [ActivityAction.LOGIN, ActivityAction.LOGOUT, ActivityAction.LOGIN_FAILED,
                    ActivityAction.PASSWORD_CHANGE, ActivityAction.PASSWORD_RESET]
    auth_result = await db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.action.in_(auth_actions))
    )
    auth_count = auth_result.scalar() or 0
    
    # CRUD actions count
    crud_actions = [ActivityAction.CREATE, ActivityAction.UPDATE, ActivityAction.DELETE,
                    ActivityAction.IMPORT, ActivityAction.EXPORT]
    crud_result = await db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.action.in_(crud_actions))
    )
    crud_count = crud_result.scalar() or 0
    
    # Error count
    error_result = await db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.action == ActivityAction.ERROR)
    )
    error_count = error_result.scalar() or 0
    
    # System + other count
    system_count = total - auth_count - crud_count - error_count
    
    # Today count
    from app.config import TASHKENT_TZ
    today_start = datetime.now(TASHKENT_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= today_start)
    )
    today_count = today_result.scalar() or 0
    
    return LogStatsResponse(
        total=total,
        auth_count=auth_count,
        crud_count=crud_count,
        system_count=system_count,
        error_count=error_count,
        today_count=today_count
    )


@router.get("", response_model=LogsResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action_type: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get activity logs with filtering and pagination."""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin loglarga kira oladi")
    
    # Base query
    query = select(ActivityLog).options()
    count_query = select(func.count(ActivityLog.id))
    
    # Filter by action category
    if action_type:
        if action_type == 'auth':
            actions = [ActivityAction.LOGIN, ActivityAction.LOGOUT, ActivityAction.LOGIN_FAILED,
                      ActivityAction.PASSWORD_CHANGE, ActivityAction.PASSWORD_RESET]
            query = query.where(ActivityLog.action.in_(actions))
            count_query = count_query.where(ActivityLog.action.in_(actions))
        elif action_type == 'crud':
            actions = [ActivityAction.CREATE, ActivityAction.UPDATE, ActivityAction.DELETE,
                      ActivityAction.IMPORT, ActivityAction.EXPORT]
            query = query.where(ActivityLog.action.in_(actions))
            count_query = count_query.where(ActivityLog.action.in_(actions))
        elif action_type == 'error':
            query = query.where(ActivityLog.action == ActivityAction.ERROR)
            count_query = count_query.where(ActivityLog.action == ActivityAction.ERROR)
        elif action_type == 'system':
            system_actions = [ActivityAction.SYSTEM, ActivityAction.SYNC, ActivityAction.AI_ANALYSIS,
                            ActivityAction.REPORT_GENERATE, ActivityAction.REPORT_DOWNLOAD,
                            ActivityAction.USER_ACTIVATE, ActivityAction.USER_DEACTIVATE,
                            ActivityAction.ROLE_CHANGE]
            query = query.where(ActivityLog.action.in_(system_actions))
            count_query = count_query.where(ActivityLog.action.in_(system_actions))
    
    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                ActivityLog.description.ilike(search_pattern),
                ActivityLog.entity_type.ilike(search_pattern),
                ActivityLog.ip_address.ilike(search_pattern),
            )
        )
        count_query = count_query.where(
            or_(
                ActivityLog.description.ilike(search_pattern),
                ActivityLog.entity_type.ilike(search_pattern),
                ActivityLog.ip_address.ilike(search_pattern),
            )
        )
    
    # User filter
    if user_id:
        query = query.where(ActivityLog.user_id == user_id)
        count_query = count_query.where(ActivityLog.user_id == user_id)
    
    # Entity type filter
    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)
        count_query = count_query.where(ActivityLog.entity_type == entity_type)
    
    # Date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.where(ActivityLog.created_at >= start_dt)
            count_query = count_query.where(ActivityLog.created_at >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.where(ActivityLog.created_at <= end_dt)
            count_query = count_query.where(ActivityLog.created_at <= end_dt)
        except:
            pass
    
    # Get total
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Order by newest first + pagination
    query = query.order_by(desc(ActivityLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = []
    for log in logs:
        items.append(LogEntryResponse(
            id=log.id,
            created_at=log.created_at,
            action=log.action.value if isinstance(log.action, ActivityAction) else str(log.action),
            description=log.description,
            user_id=log.user_id,
            user_name=log.user.name if log.user else "Tizim",
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            old_data=log.old_data,
            new_data=log.new_data,
            context=log.context,
        ))
    
    total_pages = max(1, (total + page_size - 1) // page_size)
    
    return LogsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific log entry."""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin")
    
    result = await db.execute(select(ActivityLog).where(ActivityLog.id == log_id))
    log_entry = result.scalar_one_or_none()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log topilmadi")
    
    await db.delete(log_entry)
    await db.commit()
    return {"message": "Log o'chirildi"}


@router.delete("")
async def clear_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clear all logs."""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin")
    
    from sqlalchemy import delete
    await db.execute(delete(ActivityLog))
    await db.commit()
    return {"message": "Barcha loglar tozalandi"}
