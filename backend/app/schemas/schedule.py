"""
UniControl - Schedule Schemas
=============================
Pydantic schemas for schedule-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.schedule import WeekDay, ScheduleType, WeekType


class ScheduleBase(BaseModel):
    """Base schedule schema."""
    group_id: int
    subject: str = Field(..., min_length=1, max_length=200)
    subject_code: Optional[str] = Field(None, max_length=50)
    schedule_type: ScheduleType = ScheduleType.LECTURE
    day_of_week: Optional[WeekDay] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time
    lesson_number: Optional[int] = None
    week_type: WeekType = WeekType.ALL
    room: Optional[str] = Field(None, max_length=100)
    building: Optional[str] = Field(None, max_length=100)
    teacher_name: Optional[str] = Field(None, max_length=150)
    teacher_id: Optional[int] = None
    description: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=20)


class ScheduleCreate(ScheduleBase):
    """Schema for creating schedule."""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating schedule."""
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    subject_code: Optional[str] = Field(None, max_length=50)
    schedule_type: Optional[ScheduleType] = None
    day_of_week: Optional[WeekDay] = None
    specific_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    lesson_number: Optional[int] = None
    week_type: Optional[WeekType] = None
    room: Optional[str] = Field(None, max_length=100)
    building: Optional[str] = Field(None, max_length=100)
    teacher_name: Optional[str] = Field(None, max_length=150)
    teacher_id: Optional[int] = None
    description: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    cancellation_reason: Optional[str] = None


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: int
    group_id: int
    group_name: Optional[str] = None
    subject: str
    subject_code: Optional[str] = None
    schedule_type: ScheduleType
    day_of_week: Optional[WeekDay] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time
    time_range: str
    duration_minutes: int
    lesson_number: Optional[int] = None
    week_type: WeekType = WeekType.ALL
    room: Optional[str] = None
    building: Optional[str] = None
    location: Optional[str] = None
    teacher_name: Optional[str] = None
    teacher_id: Optional[int] = None
    description: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    is_cancelled: bool
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ScheduleListResponse(BaseModel):
    """Schema for paginated schedule list."""
    items: List[ScheduleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WeekSchedule(BaseModel):
    """Schema for week schedule."""
    monday: List[ScheduleResponse] = []
    tuesday: List[ScheduleResponse] = []
    wednesday: List[ScheduleResponse] = []
    thursday: List[ScheduleResponse] = []
    friday: List[ScheduleResponse] = []
    saturday: List[ScheduleResponse] = []
    sunday: List[ScheduleResponse] = []


class DaySchedule(BaseModel):
    """Schema for day schedule."""
    date: date
    day_of_week: WeekDay
    schedules: List[ScheduleResponse] = []


class CancelSchedule(BaseModel):
    """Schema for cancelling a schedule."""
    cancellation_reason: str
