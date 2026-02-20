"""
UniControl - Attendance Model
=============================
Attendance tracking model for students.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from enum import Enum
from typing import Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy import String, Integer, DateTime, Date, Time, ForeignKey, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class AttendanceStatus(str, Enum):
    """Attendance status enum."""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(Base):
    """
    Attendance model.
    
    Tracks daily attendance for each student.
    """
    
    __tablename__ = "attendances"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Student
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Student ID"
    )
    
    # Date
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Attendance date"
    )
    
    # Status
    status: Mapped[AttendanceStatus] = mapped_column(
        SAEnum(AttendanceStatus),
        nullable=False,
        default=AttendanceStatus.ABSENT,
        comment="Attendance status"
    )
    
    # Check-in/out times
    check_in_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
        comment="Check-in time"
    )
    check_out_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
        comment="Check-out time"
    )
    
    # Late info
    late_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Minutes late"
    )
    
    # Subject/lesson
    subject: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Subject/lesson name"
    )
    lesson_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Lesson number (para)"
    )
    
    # Notes
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes"
    )
    
    # Excuse reason
    excuse_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for excused absence"
    )
    
    # Recorded by
    recorded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who recorded attendance"
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
    
    # Telegram notification tracking - prevents bot from re-sending what backend already sent
    telegram_notified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        comment="Whether Telegram notification was already sent by backend"
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="attendances",
        lazy="selectin"
    )
    
    recorded_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[recorded_by],
        lazy="noload"
    )
    
    # Indexes and constraints
    __table_args__ = (
        sa.Index("ix_attendance_date_status", "date", "status"),
        sa.Index("ix_attendance_student_date", "student_id", "date"),
        {"sqlite_autoincrement": True},
    )
    
    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, student_id={self.student_id}, date={self.date}, status={self.status.value})>"
    
    @property
    def student_name(self) -> Optional[str]:
        """Get student full name."""
        if self.student:
            return getattr(self.student, 'full_name', None) or getattr(self.student, 'name', None)
        return None
    
    @property
    def is_present(self) -> bool:
        """Check if student was present."""
        return self.status == AttendanceStatus.PRESENT
    
    @property
    def is_absent(self) -> bool:
        """Check if student was absent."""
        return self.status == AttendanceStatus.ABSENT
    
    @property
    def is_late(self) -> bool:
        """Check if student was late."""
        return self.status == AttendanceStatus.LATE
    
    @property
    def is_excused(self) -> bool:
        """Check if absence was excused."""
        return self.status == AttendanceStatus.EXCUSED
