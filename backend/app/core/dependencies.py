"""
UniControl - Dependencies
=========================
FastAPI dependency injection utilities.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole
from app.core.exceptions import UnauthorizedException, ForbiddenException


# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: The HTTP Bearer credentials
        db: Database session
        
    Returns:
        The current user
        
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
    
    # Get user ID from token
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("User not found")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are active.
    
    Args:
        current_user: The current user from token
        
    Returns:
        The active user
        
    Raises:
        ForbiddenException: If user is not active
    """
    if not current_user.is_active:
        raise ForbiddenException("User account is deactivated")
    
    return current_user


def require_role(*roles: UserRole):
    """
    Dependency to require specific user roles.
    
    Args:
        roles: Allowed roles
        
    Returns:
        A dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Access denied. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    
    return role_checker


# Pre-built role dependencies
async def require_superadmin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require superadmin role."""
    if current_user.role != UserRole.SUPERADMIN:
        raise ForbiddenException("Superadmin access required")
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin or higher role."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        raise ForbiddenException("Admin access required")
    return current_user


async def require_leader(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require leader or higher role."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.LEADER]:
        raise ForbiddenException("Leader access required")
    return current_user


async def require_teacher(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require teacher role or academic affairs."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.TEACHER, UserRole.ACADEMIC_AFFAIRS]:
        raise ForbiddenException("Teacher access required")
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get user if authenticated, otherwise return None.
    
    Useful for endpoints that work differently for authenticated users.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    return result.scalar_one_or_none()


class RoleChecker:
    """
    Class-based dependency for checking roles.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(RoleChecker([UserRole.ADMIN]))):
            ...
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException(
                f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user
