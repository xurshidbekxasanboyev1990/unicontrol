"""
SystemSettings - Tizim sozlamalari modeli
==========================================
Singleton pattern - faqat bitta row bo'ladi (id=1)
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, Text
from app.database import Base


class SystemSettings(Base):
    """
    Tizim sozlamalari - barcha global sozlamalarni saqlaydi.
    Singleton: faqat id=1 row ishlatiladi.
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, default=1)
    
    # Muassasa ma'lumotlari
    institution_name = Column(String(255), default="UniControl", nullable=False)
    institution_logo = Column(Text, nullable=True)
    institution_address = Column(Text, nullable=True)
    institution_phone = Column(String(50), nullable=True)
    institution_email = Column(String(255), nullable=True)
    
    # O'quv yili va semestr
    academic_year = Column(String(20), default="2025-2026", nullable=False)
    semester = Column(String(5), default="2", nullable=False)
    
    # Davomat sozlamalari
    attendance_threshold = Column(Integer, default=80, nullable=False)
    late_minutes_threshold = Column(Integer, default=15, nullable=False)
    
    # Ish vaqti
    working_hours_start = Column(String(10), default="08:00", nullable=False)
    working_hours_end = Column(String(10), default="18:00", nullable=False)
    
    # Integratsiyalar
    telegram_bot_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    sms_notifications_enabled = Column(Boolean, default=False, nullable=False)
    ai_analysis_enabled = Column(Boolean, default=True, nullable=False)
    
    # Interfeys
    language = Column(String(10), default="uz", nullable=False)
    timezone = Column(String(50), default="Asia/Tashkent", nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    
    # Qo'shimcha sozlamalar (JSON)
    extra = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<SystemSettings(id={self.id}, institution={self.institution_name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "institution_name": self.institution_name,
            "institution_logo": self.institution_logo,
            "institution_address": self.institution_address,
            "institution_phone": self.institution_phone,
            "institution_email": self.institution_email,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "attendance_threshold": self.attendance_threshold,
            "late_minutes_threshold": self.late_minutes_threshold,
            "working_hours_start": self.working_hours_start,
            "working_hours_end": self.working_hours_end,
            "telegram_bot_enabled": self.telegram_bot_enabled,
            "email_notifications_enabled": self.email_notifications_enabled,
            "sms_notifications_enabled": self.sms_notifications_enabled,
            "ai_analysis_enabled": self.ai_analysis_enabled,
            "language": self.language,
            "timezone": self.timezone,
            "theme": self.theme,
            "extra": self.extra or {},
        }
