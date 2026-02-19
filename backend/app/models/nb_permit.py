"""
UniControl - NB (Akademik Qarzdorlik) Permit Model
=====================================================
NB Permit (Akademik Atrabotka Ruxsatnomasi) model.
Registrar office issues permits for students with NB (academic debt).
The permit goes to the teacher, student completes the retake,
teacher confirms, and the permit check updates accordingly.

Each permit has a unique secure code to prevent forgery.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
import hashlib
import secrets

from app.config import TASHKENT_TZ
from app.database import Base


class PermitStatus(str, enum.Enum):
    """NB Permit status."""
    ISSUED = "issued"           # Registrator tomonidan berilgan
    PENDING = "pending"         # O'qituvchiga yuborilgan, kutilmoqda
    IN_PROGRESS = "in_progress" # Talaba topshirmoqda
    APPROVED = "approved"       # O'qituvchi tasdiqlagan — NB oqlangan
    REJECTED = "rejected"       # O'qituvchi rad etgan
    EXPIRED = "expired"         # Muddati o'tgan
    CANCELLED = "cancelled"     # Bekor qilingan


class NBPermit(Base):
    """
    NB Permit (Akademik Atrabotka Ruxsatnomasi).
    
    Flow:
    1. Registrar creates permit for student+subject
    2. Permit sent to teacher (teacher_id)
    3. Student goes to teacher with permit code
    4. Teacher updates status (approved/rejected)
    5. Check/receipt updates with final status
    """
    
    __tablename__ = "nb_permits"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Unique secure code (for check/receipt and anti-forgery)
    permit_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique secure permit code"
    )
    
    # Verification hash (to prevent tampering)
    verification_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="SHA-256 hash for verification"
    )
    
    # Student
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Student ID"
    )
    
    # Group (at time of issue)
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
        comment="Student's group at time of issue"
    )
    
    # Subject info
    subject_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Subject name"
    )
    
    # Semester
    semester: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Semester number"
    )
    
    # Academic year
    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="2025-2026",
        comment="Academic year"
    )
    
    # NB type
    nb_type: Mapped[str] = mapped_column(
        String(50),
        default="nb",
        nullable=False,
        comment="Type: nb, academic_debt, retake"
    )
    
    # Reason/description
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for NB / description"
    )
    
    # Teacher (who will accept the retake)
    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Teacher user ID who accepts retake"
    )
    teacher_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Teacher name (snapshot)"
    )
    
    # Issued by (registrar)
    issued_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="Registrar user ID who issued"
    )
    issued_by_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Registrar name (snapshot)"
    )
    
    # Dates
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date permit was issued"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Permit expiry date"
    )
    completed_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date retake was completed"
    )
    
    # Status
    status: Mapped[PermitStatus] = mapped_column(
        String(20),
        default=PermitStatus.ISSUED,
        nullable=False,
        index=True,
        comment="Permit status"
    )
    
    # Teacher's grade/result after retake
    result_grade: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Grade after retake (e.g., 60, pass, etc)"
    )
    
    # Teacher notes
    teacher_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Teacher's notes on retake"
    )
    
    # Registrar notes
    registrar_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Registrar's notes"
    )
    
    # Print count (how many times printed)
    print_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Times this permit was printed"
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
    student = relationship("Student", foreign_keys=[student_id], lazy="joined")
    group = relationship("Group", foreign_keys=[group_id], lazy="joined")
    teacher = relationship("User", foreign_keys=[teacher_id], lazy="joined")
    issuer = relationship("User", foreign_keys=[issued_by], lazy="joined")
    
    @staticmethod
    def generate_permit_code() -> str:
        """Generate a unique, secure permit code."""
        random_part = secrets.token_hex(8).upper()
        timestamp_part = datetime.now(TASHKENT_TZ).strftime("%y%m%d%H%M")
        return f"NB-{timestamp_part}-{random_part}"
    
    @staticmethod
    def generate_verification_hash(permit_code: str, student_id: int, subject_name: str, issue_date: str) -> str:
        """Generate SHA-256 verification hash to prevent forgery."""
        secret_salt = "UniControl-NB-Secure-2026"
        data = f"{permit_code}:{student_id}:{subject_name}:{issue_date}:{secret_salt}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify(self) -> bool:
        """Verify permit authenticity."""
        expected = self.generate_verification_hash(
            self.permit_code, self.student_id, self.subject_name, str(self.issue_date)
        )
        return self.verification_hash == expected
    
    def __repr__(self):
        return f"<NBPermit(id={self.id}, code='{self.permit_code}', status={self.status})>"
