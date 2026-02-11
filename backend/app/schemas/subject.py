"""
Subject & Direction Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Subject Schemas ============

class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = None
    description: Optional[str] = None
    credits: int = 0
    hours_per_week: int = 2


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    hours_per_week: Optional[int] = None
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubjectListResponse(BaseModel):
    items: List[SubjectResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ============ Direction Schemas ============

class DirectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = None
    description: Optional[str] = None
    duration_years: int = 4


class DirectionCreate(DirectionBase):
    pass


class DirectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = None
    description: Optional[str] = None
    duration_years: Optional[int] = None
    is_active: Optional[bool] = None


class DirectionResponse(DirectionBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    subject_ids: Optional[List[int]] = []
    
    class Config:
        from_attributes = True


class DirectionListResponse(BaseModel):
    items: List[DirectionResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ============ Direction Subject Schemas ============

class DirectionSubjectUpdate(BaseModel):
    subject_ids: List[int]
