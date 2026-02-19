"""
UniControl - User Model
========================
User model for authentication and authorization.
Supports multiple roles: student, leader, admin, superadmin.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON
import enum

from app.config import TASHKENT_TZ
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    LEADER = "leader"
    TEACHER = "teacher"
    ACADEMIC_AFFAIRS = "academic_affairs"
    REGISTRAR_OFFICE = "registrar_office"
    DEAN = "dean"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base):
    """
    User model for authentication.
    
    Attributes:
        id: Primary key
        login: Unique login username
        email: User email (optional)
        password_hash: Hashed password (bcrypt)
        role: User role (student, leader, admin, superadmin)
        name: Full name
        phone: Phone number
        avatar: Avatar URL or path
        is_active: Account status
        is_verified: Email verification status
        last_login: Last login timestamp
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Authentication fields
    login: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Unique login username"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), 
        unique=True, 
        nullable=True, 
        index=True,
        comment="User email address"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Bcrypt hashed password"
    )
    
    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.STUDENT,
        nullable=False,
        index=True,
        comment="User role for authorization"
    )
    
    # Profile information
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Full name"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="Phone number"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True,
        comment="Avatar URL or file path"
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Account active status"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Email verification status"
    )
    is_first_login: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="True if user needs to change password on first login"
    )
    
    # Timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Last successful login"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False,
        comment="Account creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(TASHKENT_TZ), 
        onupdate=lambda: datetime.now(TASHKENT_TZ),
        nullable=False,
        comment="Last update timestamp"
    )
    
    # Plain password storage (for admin view - educational institution requirement)
    plain_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Plain text password for admin viewing (educational use)"
    )
    
    # Refresh token for mobile/web sessions
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Current refresh token"
    )
    
    # Additional settings as JSON
    settings: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User settings as JSON"
    )
    
    # Device tokens for push notifications
    device_tokens: Mapped[Optional[List[Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        comment="Device tokens for push notifications"
    )
    
    # Relationships
    # student: Mapped[Optional["Student"]] = relationship(
    #     "Student", 
    #     back_populates="user", 
    #     uselist=False
    # )
    
    # notifications_sent: Mapped[List["Notification"]] = relationship(
    #     "Notification",
    #     back_populates="sender",
    #     foreign_keys="Notification.sender_id"
    # )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, login='{self.login}', role={self.role.value})>"
    
    @property
    def full_name(self) -> str:
        """Alias for name - backward compatibility."""
        return self.name
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.role == UserRole.STUDENT
    
    @property
    def is_leader(self) -> bool:
        """Check if user is a group leader."""
        return self.role == UserRole.LEADER
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is a teacher."""
        return self.role == UserRole.TEACHER
    
    @property
    def is_academic_affairs(self) -> bool:
        """Check if user is academic affairs."""
        return self.role == UserRole.ACADEMIC_AFFAIRS
    
    @property
    def is_registrar_office(self) -> bool:
        """Check if user is registrar office."""
        return self.role == UserRole.REGISTRAR_OFFICE
    
    @property
    def is_dean(self) -> bool:
        """Check if user is dean office."""
        return self.role == UserRole.DEAN
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_superadmin(self) -> bool:
        """Check if user is a superadmin."""
        return self.role == UserRole.SUPERADMIN
    
    @property
    def can_manage_students(self) -> bool:
        """Check if user can manage students."""
        return self.role in [UserRole.TEACHER, UserRole.LEADER, UserRole.ADMIN, UserRole.SUPERADMIN]
    
    @property
    def can_manage_groups(self) -> bool:
        """Check if user can manage groups."""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    @property
    def can_manage_admins(self) -> bool:
        """Check if user can manage other admins."""
        return self.role == UserRole.SUPERADMIN
