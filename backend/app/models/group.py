"""
UniControl - Group Model
=========================
Group model for managing student groups/classes.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.schedule import Schedule


class Group(Base):
    """
    Group/Class model.
    
    Attributes:
        id: Primary key
        name: Group name (e.g., KI_25-04)
        faculty: Faculty name
        year: Study year (1-4)
        leader_id: Group leader student ID
        contract_amount: Standard contract amount for group
        description: Group description
        is_active: Group status
    """
    
    __tablename__ = "groups"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Group information
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Group name (e.g., KI_25-04)"
    )
    faculty: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Faculty name"
    )
    course_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Course year (1-6)"
    )
    
    # Group leader (references Student)
    leader_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        comment="Group leader student ID"
    )
    
    # Contract information
    contract_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Standard contract amount for group"
    )
    
    # Additional info
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Group description"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Group active status"
    )
    
    # KUAF Mutoola integration
    mutoola_group_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="KUAF Mutoola group ID for sync"
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
    
    # Relationships - use lazy="select" (default) to avoid auto-loading
    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="group",
        foreign_keys="Student.group_id",
        lazy="select"  # Changed from selectin - don't auto-load
    )
    
    leader: Mapped[Optional["Student"]] = relationship(
        "Student",
        foreign_keys=[leader_id],
        lazy="select",  # Changed from joined
        post_update=True
    )
    
    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule",
        back_populates="group",
        lazy="select"  # Changed from selectin
    )
    
    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name='{self.name}', faculty='{self.faculty}')>"
    
    @property
    def code(self) -> str:
        """Get group code (alias for name, used by Telegram bot)."""
        return self.name
    
    @property
    def student_count(self) -> int:
        """Get number of students in group (safe for async - doesn't trigger lazy load)."""
        try:
            return len(self.students) if self.students else 0
        except Exception:
            return 0
    
    @property
    def leader_name(self) -> Optional[str]:
        """Get leader's name (safe for async - doesn't trigger lazy load)."""
        try:
            return self.leader.name if self.leader else None
        except Exception:
            return None
