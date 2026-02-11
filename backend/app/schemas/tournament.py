"""
Tournament (Turnir) Schemas
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ Tournament Schemas ============

class TournamentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = "sport"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_deadline: Optional[date] = None
    location: Optional[str] = None
    max_participants: int = 100
    prize: Optional[str] = None
    rules: Optional[str] = None


class TournamentCreate(TournamentBase):
    pass


class TournamentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_deadline: Optional[date] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    prize: Optional[str] = None
    rules: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class TournamentResponse(TournamentBase):
    id: int
    status: str = "upcoming"
    is_active: bool = True
    registrations_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TournamentListResponse(BaseModel):
    items: List[TournamentResponse]
    total: int
    page: int = 1
    page_size: int = 50


# ============ Registration Schemas ============

class TournamentRegister(BaseModel):
    student_id: int


class TournamentRegistrationResponse(BaseModel):
    id: int
    tournament_id: int
    student_id: int
    registered_at: datetime
    status: str
    position: Optional[int] = None
    score: Optional[int] = None
    
    class Config:
        from_attributes = True
