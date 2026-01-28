"""
UniControl - Group Routes
=========================
Group management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.group_service import GroupService
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupListResponse,
    GroupStats,
)
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter()


@router.get("", response_model=GroupListResponse)
@router.get("/", response_model=GroupListResponse, include_in_schema=False)
async def list_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    course_year: Optional[int] = None,
    faculty: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List groups with pagination and filters.
    """
    service = GroupService(db)
    groups, total = await service.list_groups(
        page=page,
        page_size=page_size,
        course_year=course_year,
        faculty=faculty,
        is_active=is_active,
        search=search
    )
    
    # Add students_count to each group
    items = []
    for g in groups:
        response = GroupResponse.model_validate(g)
        response.students_count = await service.get_students_count(g.id)
        items.append(response)
    
    return GroupListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new group.
    
    Requires admin role.
    """
    service = GroupService(db)
    group = await service.create(group_data)
    return GroupResponse.model_validate(group)


@router.get("/statistics", response_model=GroupStats)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get group statistics.
    
    Requires admin role.
    """
    service = GroupService(db)
    return await service.get_statistics()


@router.get("/active", response_model=list)
async def get_active_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active groups.
    """
    service = GroupService(db)
    groups = await service.get_all_active()
    return [GroupResponse.model_validate(g) for g in groups]


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get group by ID.
    """
    service = GroupService(db)
    group = await service.get_by_id(group_id)
    if not group:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Group not found")
    
    response = GroupResponse.model_validate(group)
    response.students_count = await service.get_students_count(group_id)
    return response


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update group.
    
    Requires admin role.
    """
    service = GroupService(db)
    group = await service.update(group_id, group_data)
    return GroupResponse.model_validate(group)


@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete group.
    
    Requires admin role. Group must have no students.
    """
    service = GroupService(db)
    await service.delete(group_id)
    return {"message": "Group deleted successfully"}


@router.post("/{group_id}/set-leader", response_model=GroupResponse)
async def set_group_leader(
    group_id: int,
    leader_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Set or unset group leader.
    
    Requires admin role.
    """
    service = GroupService(db)
    group = await service.set_leader(group_id, leader_id)
    return GroupResponse.model_validate(group)


@router.get("/faculty/{faculty}", response_model=list)
async def get_groups_by_faculty(
    faculty: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all groups in a faculty.
    """
    service = GroupService(db)
    groups = await service.get_by_faculty(faculty)
    return [GroupResponse.model_validate(g) for g in groups]


@router.get("/search", response_model=GroupListResponse)
async def search_groups(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search groups by code or name.
    """
    service = GroupService(db)
    groups, total = await service.list_groups(
        page=1,
        page_size=20,
        search=q
    )
    
    items = []
    for g in groups:
        response = GroupResponse.model_validate(g)
        response.students_count = await service.get_students_count(g.id)
        items.append(response)
    
    return GroupListResponse(
        items=items,
        total=total,
        page=1,
        page_size=20,
        total_pages=1
    )


@router.get("/code/{code}", response_model=GroupResponse)
async def get_group_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get group by exact code.
    """
    service = GroupService(db)
    group = await service.get_by_code(code.upper())
    if not group:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Group with code '{code}' not found")
    
    response = GroupResponse.model_validate(group)
    response.students_count = await service.get_students_count(group.id)
    return response
