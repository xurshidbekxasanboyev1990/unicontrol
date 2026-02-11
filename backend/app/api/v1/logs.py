"""
Logs API Routes (SuperAdmin only)
"""

from typing import Optional, List
from datetime import datetime
from app.config import now_tashkent
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.core.dependencies import get_current_active_user

router = APIRouter()


class LogEntry(BaseModel):
    """Log entry model"""
    id: int
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, DEBUG
    action: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[str] = None
    module: Optional[str] = None

    class Config:
        from_attributes = True


class LogsResponse(BaseModel):
    """Logs list response"""
    items: List[LogEntry]
    total: int
    page: int
    limit: int


# In-memory logs (production da database yoki log fayllardan o'qish kerak)
_logs: List[LogEntry] = [
    LogEntry(
        id=1,
        timestamp=now_tashkent(),
        level="INFO",
        action="System started",
        user_id=None,
        user_name="System",
        ip_address="127.0.0.1",
        details="UniControl backend started successfully",
        module="main"
    ),
    LogEntry(
        id=2,
        timestamp=now_tashkent(),
        level="INFO",
        action="Database connected",
        user_id=None,
        user_name="System",
        ip_address="127.0.0.1",
        details="SQLite database connection established",
        module="database"
    )
]


@router.get("", response_model=LogsResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    level: Optional[str] = None,
    module: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Tizim loglarini olish (faqat super_admin)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin loglarga kira oladi")
    
    # Filter logs
    filtered = _logs.copy()
    
    if level:
        filtered = [l for l in filtered if l.level == level]
    if module:
        filtered = [l for l in filtered if l.module == module]
    if search:
        search_lower = search.lower()
        filtered = [l for l in filtered if search_lower in (l.action or "").lower() or search_lower in (l.details or "").lower()]
    if start_date:
        filtered = [l for l in filtered if l.timestamp >= start_date]
    if end_date:
        filtered = [l for l in filtered if l.timestamp <= end_date]
    
    # Pagination
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    items = filtered[start:end]
    
    return LogsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Logni o'chirish (faqat super_admin)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin loglarga kira oladi")
    
    global _logs
    _logs = [l for l in _logs if l.id != log_id]
    return {"message": "Log o'chirildi"}


@router.delete("")
async def clear_logs(
    current_user: User = Depends(get_current_active_user)
):
    """Barcha loglarni tozalash (faqat super_admin)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Faqat super admin loglarga kira oladi")
    
    global _logs
    _logs = []
    return {"message": "Barcha loglar tozalandi"}
