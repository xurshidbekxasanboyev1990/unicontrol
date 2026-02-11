"""
Club (To'garak) Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Club Schemas ============

class ClubBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    teacher: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None
    price: Optional[float] = 0
    room: Optional[str] = None
    category: str = "fan"
    max_members: int = 30


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    teacher: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None
    price: Optional[float] = None
    room: Optional[str] = None
    category: Optional[str] = None
    max_members: Optional[int] = None
    is_active: Optional[bool] = None


class ClubResponse(ClubBase):
    id: int
    members_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClubListResponse(BaseModel):
    items: List[ClubResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ============ Club Member Schemas ============

class ClubMemberCreate(BaseModel):
    club_id: int
    student_id: int


class ClubMemberResponse(BaseModel):
    id: int
    club_id: int
    student_id: int
    joined_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
