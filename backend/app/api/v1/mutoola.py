"""
UniControl - Mutoola Routes
===========================
KUAF Mutoola API integration endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.mutoola_service import MutoolaService
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter()


# Request/Response Models
class SyncRequest(BaseModel):
    """Request for sync operation."""
    entity_type: str  # students, groups, schedules, all
    group_id: Optional[int] = None
    force: bool = False


class SyncResponse(BaseModel):
    """Response for sync operation."""
    success: bool
    synced_count: int
    failed_count: int
    errors: list[str] = []
    sync_id: Optional[int] = None


class MutoolaStudentResponse(BaseModel):
    """Mutoola student data."""
    hemis_id: str
    full_name: str
    group_name: str
    course: int
    faculty: str
    status: str


class MutoolaGroupResponse(BaseModel):
    """Mutoola group data."""
    code: str
    name: str
    faculty: str
    course: int
    student_count: int


class SyncHistoryResponse(BaseModel):
    """Sync history item."""
    id: int
    entity_type: str
    sync_type: str
    status: str
    records_synced: int
    errors: Optional[str]
    started_at: str
    completed_at: Optional[str]


@router.post("/sync", response_model=SyncResponse)
async def sync_data(
    request: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Sync data from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.sync_data(
        entity_type=request.entity_type,
        group_id=request.group_id,
        force=request.force
    )


@router.post("/sync/students", response_model=SyncResponse)
async def sync_students(
    group_id: Optional[int] = None,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Sync students from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.sync_students(group_id, force)


@router.post("/sync/groups", response_model=SyncResponse)
async def sync_groups(
    faculty: Optional[str] = None,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Sync groups from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.sync_groups(faculty, force)


@router.post("/sync/schedules", response_model=SyncResponse)
async def sync_schedules(
    group_id: Optional[int] = None,
    semester: Optional[int] = None,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Sync schedules from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.sync_schedules(group_id, semester, force)


@router.get("/students", response_model=list[MutoolaStudentResponse])
async def get_mutoola_students(
    group_code: Optional[str] = None,
    faculty: Optional[str] = None,
    course: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get students directly from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_mutoola_students(
        group_code=group_code,
        faculty=faculty,
        course=course,
        page=page,
        page_size=page_size
    )


@router.get("/groups", response_model=list[MutoolaGroupResponse])
async def get_mutoola_groups(
    faculty: Optional[str] = None,
    course: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get groups directly from Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_mutoola_groups(
        faculty=faculty,
        course=course
    )


@router.get("/student/{hemis_id}", response_model=MutoolaStudentResponse)
async def get_mutoola_student(
    hemis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get student from Mutoola API by HEMIS ID.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_mutoola_student(hemis_id)


@router.get("/sync/history", response_model=list[SyncHistoryResponse])
async def get_sync_history(
    entity_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get sync history.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_sync_history(
        entity_type=entity_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )


@router.get("/sync/{sync_id}")
async def get_sync_details(
    sync_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get sync details by ID.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_sync_details(sync_id)


@router.post("/verify-connection")
async def verify_mutoola_connection(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Verify connection to Mutoola API.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.verify_connection()


@router.get("/faculties")
async def get_faculties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of faculties from Mutoola.
    """
    service = MutoolaService(db)
    return await service.get_faculties()


@router.get("/stats")
async def get_mutoola_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get Mutoola sync statistics.
    
    Requires admin role.
    """
    service = MutoolaService(db)
    return await service.get_sync_stats()
