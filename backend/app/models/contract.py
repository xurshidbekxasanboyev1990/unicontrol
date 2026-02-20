"""
UniControl - Contract Model
============================
Contract/payment data model for managing student contract information.
Supports yearly academic contract data (e.g., 2025-2026 academic year).

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.group import Group


class Contract(Base):
    """
    Contract model — stores student contract/payment data per academic year.
    
    Excel columns mapping:
    - To'liq ismi -> student.name (matched via jshshir)
    - JSHSHIR-kod -> student.jshshir
    - Pasport seriya va raqami -> student.passport
    - Telefon raqami -> student.phone
    - Kurs -> course
    - Talaba xolati -> student_status
    - Guruh -> group (matched by name)
    - Yo'nalishi -> direction
    - Ta'lim shakli -> education_form
    - Shartnoma bo'yicha yillik kontrakt summasi -> contract_amount
    - Grand (Foizda) -> grant_percentage
    - Grand (Summada) -> grant_amount
    - Shartnoma bo'yicha qarzdorlik summasi -> debt_amount
    - Foizda (Jami) -> payment_percentage
    - To'lov summa (Jami) -> total_paid
    - Qaytarib berilgan summa (Jami) -> refund_amount
    - O'quv yili boshiga qoldiq -> year_start_balance
    - O'quv yili yakuniga qoldiq -> year_end_balance
    """
    
    __tablename__ = "contracts"
    
    # Unique constraint: one contract per student per academic year
    __table_args__ = (
        UniqueConstraint('student_id', 'academic_year', name='uq_contract_student_year'),
    )
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Link to Student
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Student ID"
    )
    
    # Academic year (e.g., "2025-2026")
    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="2025-2026",
        comment="Academic year (e.g., 2025-2026)"
    )
    
    # Student info at time of contract
    course: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Course (e.g., 1-kurs, 2-kurs)"
    )
    student_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Student status (O'qimoqda, Akademik ta'til, etc.)"
    )
    direction: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Direction (Yo'nalish - Davolash ishi, etc.)"
    )
    education_form: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Education form (Kunduzgi, Sirtqi, etc.)"
    )
    
    # Contract amounts
    contract_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Annual contract amount (Shartnoma bo'yicha yillik kontrakt summasi)"
    )
    
    # Grant info
    grant_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        default=0,
        comment="Grant percentage (Grand - Foizda)"
    )
    grant_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Grant amount (Grand - Summada)"
    )
    
    # Debt and payment
    debt_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Debt amount (Shartnoma bo'yicha qarzdorlik summasi)"
    )
    payment_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        default=0,
        comment="Payment percentage (Foizda Jami)"
    )
    total_paid: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Total paid amount (To'lov summa Jami)"
    )
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Refund amount (Qaytarib berilgan summa)"
    )
    
    # Balance
    year_start_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Balance at start of academic year"
    )
    year_end_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Balance at end of academic year"
    )
    
    # Extra note
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes"
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
    student: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[student_id],
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, student_id={self.student_id}, year='{self.academic_year}', amount={self.contract_amount})>"
    
    @property
    def student_name(self) -> Optional[str]:
        """Get student name."""
        return self.student.name if self.student else None
    
    @property
    def student_jshshir(self) -> Optional[str]:
        """Get student JSHSHIR."""
        return self.student.jshshir if self.student else None
    
    @property
    def group_name(self) -> Optional[str]:
        """Get student's group name."""
        if self.student and self.student.group:
            return self.student.group.name
        return None
    
    @property
    def remaining_amount(self) -> Decimal:
        """Get remaining amount to pay."""
        return self.contract_amount - self.total_paid
    
    @property
    def is_fully_paid(self) -> bool:
        """Check if contract is fully paid."""
        return self.total_paid >= self.contract_amount
