"""
UniControl - Teacher Workload Model
====================================
Stores teacher workload/schedule data imported from Excel.
Each row = one teacher's one lesson slot per week.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config import now_tashkent
from app.database import Base


class TeacherWorkload(Base):
    """
    Teacher Workload model.
    
    Stores parsed teacher schedule data from Excel.
    Teachers can search and view their own workload.
    """
    __tablename__ = "teacher_workload"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Teacher info
    teacher_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    teacher_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Asosiy, Tashqi, Ichki, etc.
    
    # Schedule info
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)  # monday, tuesday, etc.
    day_name_uz: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Dushanba, Seshanba, etc.
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-6
    start_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 08:30
    end_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 09:50
    
    # Group/subject info
    groups: Mapped[str] = mapped_column(String(500), nullable=False)  # Group name(s), e.g. "ING-24-10" or "IQ-25-01-02"
    is_busy: Mapped[bool] = mapped_column(Boolean, default=False)  # True if marked as "BAND"
    
    # Metadata
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=now_tashkent)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def __repr__(self):
        return f"<TeacherWorkload {self.teacher_name} | {self.day_of_week} para-{self.lesson_number} | {self.groups}>"
