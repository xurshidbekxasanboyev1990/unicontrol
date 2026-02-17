"""
UniControl - User Service
=========================
Handles user management operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException


class UserService:
    """User management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        List users with pagination and filters.
        
        Returns:
            Tuple of (users list, total count)
        """
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Apply filters
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.name.ilike(search_filter)) | 
                (User.email.ilike(search_filter)) |
                (User.login.ilike(search_filter))
            )
            count_query = count_query.where(
                (User.name.ilike(search_filter)) | 
                (User.email.ilike(search_filter)) |
                (User.login.ilike(search_filter))
            )
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check email uniqueness
        existing = await self.get_by_email(user_data.email)
        if existing:
            raise ConflictException("Email already registered")
        
        # Check login uniqueness
        login_value = user_data.login or user_data.email
        existing_login = await self.db.execute(
            select(User).where(User.login == login_value)
        )
        if existing_login.scalar_one_or_none():
            raise ConflictException("Login already registered")
        
        user = User(
            login=user_data.login or user_data.email,
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            plain_password=user_data.password,
            role=user_data.role,
            phone=user_data.phone,
            avatar=user_data.avatar,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update(
        self,
        user_id: int,
        user_data: UserUpdate,
        current_user: User
    ) -> User:
        """Update user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Check permissions
        if current_user.role != UserRole.SUPERADMIN:
            if current_user.id != user_id:
                raise ForbiddenException("Cannot update other users")
            # Regular users can't change their role
            if user_data.role is not None:
                raise ForbiddenException("Cannot change own role")
        
        # Check email uniqueness if changing
        if user_data.email and user_data.email != user.email:
            existing = await self.get_by_email(user_data.email)
            if existing:
                raise ConflictException("Email already in use")
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete(self, user_id: int, current_user: User) -> bool:
        """Delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Cannot delete yourself
        if user_id == current_user.id:
            raise ForbiddenException("Cannot delete yourself")
        
        # Cannot delete superadmin
        if user.role == UserRole.SUPERADMIN:
            raise ForbiddenException("Cannot delete superadmin")
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def activate(self, user_id: int) -> User:
        """Activate user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user.is_active = True
        await self.db.commit()
        
        return user
    
    async def deactivate(self, user_id: int, current_user: User) -> User:
        """Deactivate user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        if user_id == current_user.id:
            raise ForbiddenException("Cannot deactivate yourself")
        
        if user.role == UserRole.SUPERADMIN:
            raise ForbiddenException("Cannot deactivate superadmin")
        
        user.is_active = False
        await self.db.commit()
        
        return user
    
    async def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (admin action)."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user.password_hash = get_password_hash(new_password)
        user.plain_password = new_password
        await self.db.commit()
        
        return True
    
    async def get_admins(self) -> List[User]:
        """Get all admin users."""
        result = await self.db.execute(
            select(User).where(
                User.role.in_([UserRole.SUPERADMIN, UserRole.ADMIN])
            ).order_by(User.name)
        )
        return list(result.scalars().all())
    
    async def get_leaders(self) -> List[User]:
        """Get all leader users."""
        result = await self.db.execute(
            select(User).where(
                User.role == UserRole.LEADER
            ).order_by(User.name)
        )
        return list(result.scalars().all())
