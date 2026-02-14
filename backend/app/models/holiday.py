"""
UniControl - Holiday/Off-Day Model
====================================
Model for managing holidays and off-days (dam olish kunlari).

Admin/Super admin can mark date ranges as holidays.
These days are excluded from attendance, schedule display, and AI analysis.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.config import TASHKENT_TZ
from app.database import Base


class HolidayType(str, enum.Enum):
    """Dam olish turi"""
    HOLIDAY = "holiday"          # Bayram (rasmiy bayram)
    OFF_DAY = "off_day"          # Dam olish kuni
    EXAM_PERIOD = "exam_period"  # Imtihon davri
    OTHER = "other"              # Boshqa


class Holiday(Base):
    """Dam olish / bayram kunlari"""
    __tablename__ = "holidays"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    holiday_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=HolidayType.HOLIDAY.value
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # user_id

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        onupdate=lambda: datetime.now(TASHKENT_TZ)
    )

    def __repr__(self):
        return f"<Holiday(id={self.id}, title='{self.title}', {self.start_date} - {self.end_date})>"
