"""
UniControl - Student Model
===========================
Student model for managing student information and contracts.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group
    from app.models.attendance import Attendance


class Student(Base):
    """
    Student model.
    
    Attributes:
        id: Primary key
        student_id: Unique student ID (e.g., ST-2024-001)
        user_id: Linked user account ID
        name: Full name
        group_id: Student's group ID
        
        Personal info:
        - phone, email, address, commute
        - passport, jshshir (PINFL)
        - birth_date, gender
        
        Contract info:
        - contract_amount, contract_paid
        
        Academic info:
        - enrollment_date, graduation_date
        - is_active, is_graduated
    """
    
    __tablename__ = "students"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Student ID
    student_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique student ID (e.g., ST-2024-001)"
    )
    
    # Link to User account
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        comment="Linked user account"
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        comment="Full name"
    )
    
    # Group
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Student's group"
    )
    
    # Contact information
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Phone number"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Email address"
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Home address"
    )
    commute: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="How student gets to university"
    )
    
    # Identity documents
    passport: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Passport series and number"
    )
    jshshir: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="JSHSHIR (PINFL)"
    )
    
    # Personal info
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date of birth"
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Gender (male/female)"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Avatar URL or file path"
    )
    
    # Contract information
    contract_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Contract amount"
    )
    contract_paid: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Amount paid"
    )
    
    # Academic info
    enrollment_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Enrollment date"
    )
    graduation_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Expected graduation date"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Active student status"
    )
    is_graduated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Graduated status"
    )
    is_leader: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Group leader status"
    )
    
    # KUAF Mutoola integration
    mutoola_student_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="KUAF Mutoola student ID for sync"
    )
    
    # Additional data as JSON
    extra_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional data as JSON"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )
    
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="students",
        foreign_keys=[group_id],
        lazy="joined"
    )
    
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        back_populates="student",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}')>"
    
    @property
    def group_name(self) -> Optional[str]:
        """Get group name."""
        return self.group.name if self.group else None
    
    @property
    def contract_remaining(self) -> Decimal:
        """Get remaining contract amount."""
        return self.contract_amount - self.contract_paid
    
    @property
    def contract_percentage(self) -> float:
        """Get contract payment percentage."""
        if self.contract_amount == 0:
            return 0
        return float(self.contract_paid / self.contract_amount * 100)
    
    @property
    def is_contract_paid(self) -> bool:
        """Check if contract is fully paid."""
        return self.contract_paid >= self.contract_amount
