"""
UniControl - User Routes
========================
User management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.dependencies import get_current_active_user, require_admin, require_superadmin
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=dict)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List users with pagination and filters.
    
    Requires admin role.
    """
    service = UserService(db)
    users, total = await service.list_users(
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
        search=search
    )
    
    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user.
    
    Requires admin role.
    """
    service = UserService(db)
    user = await service.create(user_data)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user by ID.
    
    Requires admin role.
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("User not found")
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user.
    
    Users can update their own profile.
    Admins can update any user.
    """
    service = UserService(db)
    user = await service.update(user_id, user_data, current_user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """
    Delete user.
    
    Requires superadmin role.
    """
    service = UserService(db)
    await service.delete(user_id, current_user)
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate user account.
    
    Requires admin role.
    """
    service = UserService(db)
    user = await service.activate(user_id)
    return {"message": "User activated", "user": UserResponse.model_validate(user)}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Deactivate user account.
    
    Requires admin role.
    """
    service = UserService(db)
    user = await service.deactivate(user_id, current_user)
    return {"message": "User deactivated", "user": UserResponse.model_validate(user)}


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=6),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset user's password (admin action).
    
    Requires admin role.
    """
    service = UserService(db)
    await service.reset_password(user_id, new_password)
    return {"message": "Password reset successfully"}


@router.get("/roles/admins", response_model=list)
async def get_admins(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """
    Get all admin users.
    
    Requires superadmin role.
    """
    service = UserService(db)
    admins = await service.get_admins()
    return [UserResponse.model_validate(a) for a in admins]


@router.get("/roles/leaders", response_model=list)
async def get_leaders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all leader users.
    
    Requires admin role.
    """
    service = UserService(db)
    leaders = await service.get_leaders()
    return [UserResponse.model_validate(l) for l in leaders]
