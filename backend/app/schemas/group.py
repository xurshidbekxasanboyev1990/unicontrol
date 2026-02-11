"""
UniControl - Group Schemas
==========================
Pydantic schemas for group-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, model_validator


class GroupBase(BaseModel):
    """Base group schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    course_year: int = Field(default=1, ge=1, le=6)
    department: Optional[str] = Field(None, max_length=200)
    faculty: Optional[str] = Field(None, max_length=200)
    contract_amount: Decimal = Field(default=0, ge=0)


class GroupCreate(GroupBase):
    """Schema for creating a group."""
    leader_id: Optional[int] = None


class GroupUpdate(BaseModel):
    """Schema for updating a group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    course_year: Optional[int] = Field(None, ge=1, le=6)
    department: Optional[str] = Field(None, max_length=200)
    faculty: Optional[str] = Field(None, max_length=200)
    leader_id: Optional[int] = None
    contract_amount: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class GroupResponse(BaseModel):
    """Schema for group response."""
    id: int
    name: str
    code: Optional[str] = None  # Alias for name, used by Telegram bot
    description: Optional[str] = None
    course_year: int
    department: Optional[str] = None
    faculty: Optional[str] = None
    leader_id: Optional[int] = None
    leader_name: Optional[str] = None
    contract_amount: Decimal
    students_count: int = 0
    is_active: bool
    mutoola_group_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @model_validator(mode='after')
    def set_code_from_name(self):
        """Set code as alias of name if not provided."""
        if self.code is None:
            self.code = self.name
        return self


class GroupListResponse(BaseModel):
    """Schema for paginated group list."""
    items: List[GroupResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GroupStats(BaseModel):
    """Schema for group statistics."""
    total_groups: int
    active_groups: int
    total_students: int
    total_contract_amount: Decimal
    total_contract_paid: Decimal
    groups_by_course: dict


class GroupWithStudents(GroupResponse):
    """Group with students list."""
    students: List["StudentResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Forward reference for StudentResponse
from app.schemas.student import StudentResponse
GroupWithStudents.model_rebuild()
