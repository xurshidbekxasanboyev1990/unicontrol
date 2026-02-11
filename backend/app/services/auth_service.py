"""
UniControl - Authentication Service
===================================
Handles user authentication and authorization.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.exceptions import (
    UnauthorizedException,
    BadRequestException,
    NotFoundException,
    ConflictException,
)
from app.config import settings, now_tashkent


class AuthService:
    """Authentication service class."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authenticate(self, login: str, password: str) -> User:
        """
        Authenticate user with login/email and password.
        
        Args:
            login: User's login or email
            password: User's password
            
        Returns:
            Authenticated user
            
        Raises:
            UnauthorizedException: If credentials are invalid
        """
        from sqlalchemy import or_
        
        logger.debug(f"Authenticate called: login={login}")
        
        # Find user by email or login
        result = await self.db.execute(
            select(User).where(
                or_(User.email == login, User.login == login)
            )
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.debug(f"User not found: {login}")
            raise UnauthorizedException("Login yoki parol noto'g'ri")
        
        logger.debug(f"User found: id={user.id}, login={user.login}, role={user.role}")
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"Wrong password attempt for user: {login}")
            raise UnauthorizedException("Login yoki parol noto'g'ri")
        
        logger.debug("Password verified OK")
        
        if not user.is_active:
            raise UnauthorizedException("Akkount faollashtirilmagan")
        
        # Update last login
        user.last_login = now_tashkent()
        await self.db.commit()
        
        return user
    
    async def login(self, credentials: UserLogin) -> Token:
        """
        Login user and return tokens.
        
        Args:
            credentials: Login credentials
            
        Returns:
            Token response with access and refresh tokens
        """
        user = await self.authenticate(credentials.login, credentials.password)
        
        # Create tokens
        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)
        
        # Save refresh token to DB for server-side validation
        user.refresh_token = refresh_token
        self.db.add(user)
        await self.db.flush()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def refresh_tokens(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New token response
            
        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        payload = verify_token(refresh_token, token_type="refresh")
        
        if payload is None:
            raise UnauthorizedException("Invalid or expired refresh token")
        
        user_id = payload.get("sub")
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        
        # Verify refresh token matches the one stored in DB (server-side invalidation)
        if user.refresh_token != refresh_token:
            raise UnauthorizedException("Refresh token has been revoked")
        
        # Create new tokens
        access_token = create_access_token(user.id, user.role.value)
        new_refresh_token = create_refresh_token(user.id)
        
        # Update stored refresh token (token rotation)
        user.refresh_token = new_refresh_token
        self.db.add(user)
        await self.db.flush()
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def register(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ConflictException: If email or login already exists
        """
        from sqlalchemy import or_
        
        # Check if email exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ConflictException("Email already registered")
        
        # Check if login exists
        login_value = user_data.login or user_data.email
        result = await self.db.execute(
            select(User).where(User.login == login_value)
        )
        if result.scalar_one_or_none():
            raise ConflictException("Login already registered")
        
        # Create user
        user = User(
            login=login_value,
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            phone=user_data.phone,
            avatar=user_data.avatar,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user: Current user
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            BadRequestException: If current password is wrong
        """
        if not verify_password(current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")
        
        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        
        return True
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_superadmin(
        self,
        email: str,
        password: str,
        name: str = "Super Admin"
    ) -> User:
        """
        Create superadmin user (for initial setup).
        
        Args:
            email: Admin email
            password: Admin password
            name: Admin name
            
        Returns:
            Created superadmin user
        """
        # Check if superadmin exists
        result = await self.db.execute(
            select(User).where(User.role == UserRole.SUPERADMIN)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # Create superadmin
        admin = User(
            email=email,
            name=name,
            password_hash=get_password_hash(password),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )
        
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)
        
        return admin
