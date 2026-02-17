"""
Subject (Fan) Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config import TASHKENT_TZ
from app.database import Base


class Subject(Base):
    """Fan modeli"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    credits = Column(Integer, default=0)  # Kredit soati
    hours_per_week = Column(Integer, default=2)  # Haftada necha soat
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), onupdate=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    direction_subjects = relationship("DirectionSubject", back_populates="subject", cascade="all, delete-orphan")


class Direction(Base):
    """Yo'nalish modeli"""
    __tablename__ = "directions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    duration_years = Column(Integer, default=4)  # O'qish davomiyligi (yil)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), onupdate=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    direction_subjects = relationship("DirectionSubject", back_populates="direction", cascade="all, delete-orphan")


class DirectionSubject(Base):
    """Yo'nalish va fan bog'lanishi"""
    __tablename__ = "direction_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    direction_id = Column(Integer, ForeignKey("directions.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    semester = Column(Integer, default=1)  # Qaysi semestrda
    is_required = Column(Boolean, default=True)  # Majburiy/ixtiyoriy
    
    # Relationships
    direction = relationship("Direction", back_populates="direction_subjects")
    subject = relationship("Subject", back_populates="direction_subjects")
