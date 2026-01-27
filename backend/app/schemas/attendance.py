"""
UniControl - Attendance Schemas
===============================
Pydantic schemas for attendance-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    """Base attendance schema."""
    student_id: int
    date: date
    status: AttendanceStatus = AttendanceStatus.ABSENT
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    late_minutes: int = 0
    subject: Optional[str] = None
    lesson_number: Optional[int] = None
    note: Optional[str] = None
    excuse_reason: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance."""
    pass


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance."""
    status: Optional[AttendanceStatus] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    late_minutes: Optional[int] = None
    note: Optional[str] = None
    excuse_reason: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    id: int
    student_id: int
    student_name: Optional[str] = None
    date: date
    status: AttendanceStatus
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    late_minutes: int
    subject: Optional[str] = None
    lesson_number: Optional[int] = None
    note: Optional[str] = None
    excuse_reason: Optional[str] = None
    recorded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceBatchItem(BaseModel):
    """Single item in batch attendance."""
    student_id: int
    status: AttendanceStatus = AttendanceStatus.ABSENT
    check_in_time: Optional[time] = None
    late_minutes: int = 0
    note: Optional[str] = None


class AttendanceBatch(BaseModel):
    """Schema for batch attendance recording."""
    date: date
    subject: Optional[str] = None
    lesson_number: Optional[int] = None
    attendances: List[AttendanceBatchItem]


class AttendanceReport(BaseModel):
    """Schema for attendance report."""
    date_from: date
    date_to: date
    group_id: Optional[int] = None
    student_id: Optional[int] = None


class AttendanceStats(BaseModel):
    """Schema for attendance statistics."""
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_rate: float
    late_rate: float


class DailyAttendanceSummary(BaseModel):
    """Schema for daily attendance summary."""
    date: date
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_rate: float


class StudentAttendanceSummary(BaseModel):
    """Schema for student's attendance summary."""
    student_id: int
    student_name: str
    group_name: Optional[str] = None
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_rate: float
    total_late_minutes: int
