"""
UniControl - User Schemas
=========================
Pydantic schemas for user-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.STUDENT
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    role: Optional[UserRole] = None
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordUpdate(BaseModel):
    """Schema for password update."""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: EmailStr
    name: str
    role: UserRole
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user stored in DB (includes sensitive fields)."""
    password_hash: str
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""
    login: str = Field(..., description="Username or email")
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str  # User ID as string
    role: str
    exp: Optional[int] = None
    iat: Optional[int] = None


class RefreshToken(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class UserProfile(UserResponse):
    """Extended user profile."""
    student_id: Optional[str] = None
    group_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
