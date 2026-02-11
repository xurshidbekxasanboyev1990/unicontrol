"""
UniControl - Student Schemas
============================
Pydantic schemas for student-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class StudentBase(BaseModel):
    """Base student schema."""
    name: str = Field(..., min_length=2, max_length=150)
    group_id: Optional[int] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    commute: Optional[str] = None
    passport: Optional[str] = Field(None, max_length=20)
    jshshir: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    contract_amount: Decimal = Field(default=0, ge=0)
    contract_paid: Decimal = Field(default=0, ge=0)
    enrollment_date: Optional[date] = None
    graduation_date: Optional[date] = None


class StudentCreate(StudentBase):
    """Schema for creating a student."""
    student_id: Optional[str] = None  # Auto-generated if not provided
    create_user_account: bool = False  # Create linked user account
    password: Optional[str] = Field(None, min_length=6)  # For user account


class StudentUpdate(BaseModel):
    """Schema for updating a student."""
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    group_id: Optional[int] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    commute: Optional[str] = None
    passport: Optional[str] = Field(None, max_length=20)
    jshshir: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    avatar: Optional[str] = None
    contract_amount: Optional[Decimal] = Field(None, ge=0)
    contract_paid: Optional[Decimal] = Field(None, ge=0)
    enrollment_date: Optional[date] = None
    graduation_date: Optional[date] = None
    is_active: Optional[bool] = None
    is_graduated: Optional[bool] = None
    is_leader: Optional[bool] = None


class StudentResponse(BaseModel):
    """Schema for student response."""
    id: int
    student_id: str
    name: str
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    commute: Optional[str] = None
    passport: Optional[str] = None
    jshshir: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    contract_amount: Decimal
    contract_paid: Decimal
    contract_remaining: Decimal
    contract_percentage: float
    is_contract_paid: bool
    enrollment_date: Optional[date] = None
    graduation_date: Optional[date] = None
    is_active: bool
    is_graduated: bool
    is_leader: bool
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class StudentImport(BaseModel):
    """Schema for importing student from Excel."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    passport: Optional[str] = None
    jshshir: Optional[str] = None
    birth_date: Optional[str] = None  # Will be parsed
    gender: Optional[str] = None
    group_name: Optional[str] = None  # Will be resolved to group_id
    contract_amount: Optional[float] = 0
    contract_paid: Optional[float] = 0


class StudentListResponse(BaseModel):
    """Schema for paginated student list."""
    items: List[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentStats(BaseModel):
    """Schema for student statistics."""
    total_students: int
    active_students: int
    graduated_students: int
    leaders_count: int
    total_contract_amount: Decimal
    total_contract_paid: Decimal
    payment_percentage: float


class PaymentUpdate(BaseModel):
    """Schema for updating student payment."""
    amount: Decimal = Field(..., gt=0)
    note: Optional[str] = None
