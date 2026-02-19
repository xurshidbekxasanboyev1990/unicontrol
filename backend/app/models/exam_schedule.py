"""
UniControl - Exam Schedule Model
==================================
Exam/Session schedule model for managing exam timetables.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, Time, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base


class ExamSchedule(Base):
    """
    Exam Schedule model.
    
    Manages exam timetables for groups during session period.
    """
    
    __tablename__ = "exam_schedules"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Group
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Group ID"
    )
    
    # Subject
    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Subject name"
    )
    
    # Exam type
    exam_type: Mapped[str] = mapped_column(
        String(50),
        default="exam",
        nullable=False,
        comment="Type: exam, midterm, retake, final"
    )
    
    # Date and time
    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Exam date"
    )
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment="Start time"
    )
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment="End time"
    )
    
    # Location
    room: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Room/auditorium"
    )
    building: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Building"
    )
    
    # Teacher/Examiner
    teacher_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Examiner name"
    )
    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Examiner user ID"
    )
    
    # Session info
    semester: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Semester number"
    )
    academic_year: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Academic year (e.g., 2025-2026)"
    )
    
    # Additional
    max_students: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Max students for this exam"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        onupdate=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    
    # Relationships
    group = relationship("Group", lazy="joined")
    teacher = relationship("User", foreign_keys=[teacher_id], lazy="joined")
    
    def __repr__(self) -> str:
        return f"<ExamSchedule(id={self.id}, subject='{self.subject}', date={self.exam_date})>"
    
    @property
    def group_name(self) -> Optional[str]:
        return self.group.name if self.group else None
    
    @property
    def time_range(self) -> str:
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
