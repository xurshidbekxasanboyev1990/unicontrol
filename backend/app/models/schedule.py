"""
UniControl - Schedule Model
===========================
Schedule model for class timetables.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Date, Time, ForeignKey, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ, today_tashkent
from app.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User


class WeekDay(str, Enum):
    """Week day enum."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class ScheduleType(str, Enum):
    """Schedule type enum."""
    LECTURE = "lecture"
    PRACTICE = "practice"
    LAB = "lab"
    SEMINAR = "seminar"
    EXAM = "exam"
    CONSULTATION = "consultation"


class WeekType(str, Enum):
    """Week type for biweekly rotation schedules (juft/toq hafta)."""
    ALL = "all"      # Every week (default)
    ODD = "odd"      # Toq hafta (odd weeks: 1, 3, 5...)
    EVEN = "even"    # Juft hafta (even weeks: 2, 4, 6...)


class Schedule(Base):
    """
    Schedule model.
    
    Manages class timetables for groups.
    """
    
    __tablename__ = "schedules"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Group
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Group ID"
    )
    
    # Subject info
    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Subject name"
    )
    subject_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Subject code"
    )
    
    # Schedule type
    schedule_type: Mapped[ScheduleType] = mapped_column(
        SAEnum(ScheduleType),
        nullable=False,
        default=ScheduleType.LECTURE,
        comment="Type of class"
    )
    
    # Day of week (for recurring schedules)
    day_of_week: Mapped[Optional[WeekDay]] = mapped_column(
        SAEnum(WeekDay),
        nullable=True,
        index=True,
        comment="Day of week for recurring schedule"
    )
    
    # Specific date (for one-time events)
    specific_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Specific date for one-time event"
    )
    
    # Time
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
    
    # Lesson number (para)
    lesson_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Lesson number (para)"
    )
    
    # Week type (biweekly rotation: juft/toq hafta)
    week_type: Mapped[str] = mapped_column(
        SAEnum(WeekType),
        nullable=False,
        default=WeekType.ALL,
        server_default="ALL",
        comment="Week type: all=every week, odd=toq hafta, even=juft hafta"
    )
    
    # Room/Location
    room: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Room/classroom"
    )
    building: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Building"
    )
    
    # Teacher
    teacher_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Teacher name"
    )
    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Teacher user ID"
    )
    
    # Additional info
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional description"
    )
    
    # Semester/Period
    semester: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Semester number"
    )
    academic_year: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Academic year (e.g., 2024-2025)"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Active schedule"
    )
    is_cancelled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Cancelled class"
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for cancellation"
    )
    
    # Color for UI
    color: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Color code for UI display"
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
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="schedules",
        lazy="selectin"
    )
    
    teacher: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[teacher_id],
        lazy="noload"
    )
    
    def __repr__(self) -> str:
        return f"<Schedule(id={self.id}, subject='{self.subject}', group_id={self.group_id})>"
    
    @property
    def group_name(self) -> Optional[str]:
        """Get group name from relationship."""
        return self.group.name if self.group else None
    
    @property
    def duration_minutes(self) -> int:
        """Get class duration in minutes."""
        start_dt = datetime.combine(today_tashkent(), self.start_time)
        end_dt = datetime.combine(today_tashkent(), self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)
    
    @property
    def time_range(self) -> str:
        """Get formatted time range."""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    @property
    def location(self) -> Optional[str]:
        """Get formatted location."""
        parts = []
        if self.building:
            parts.append(self.building)
        if self.room:
            parts.append(self.room)
        return ", ".join(parts) if parts else None