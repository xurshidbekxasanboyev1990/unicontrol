"""
Club (To'garak) Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.config import TASHKENT_TZ
from app.database import Base


class Club(Base):
    """To'garak modeli"""
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    teacher = Column(String(200), nullable=False)  # O'qituvchi
    phone = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    schedule = Column(String(200), nullable=True)  # Dars jadvali
    price = Column(Numeric(12, 2), default=0)  # Narxi
    room = Column(String(100), nullable=True)  # Xona
    category = Column(String(50), default='fan')  # fan, til, texnik, sport, san'at
    max_members = Column(Integer, default=30)
    members_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), onupdate=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")


class ClubMember(Base):
    """To'garak a'zosi"""
    __tablename__ = "club_members"
    
    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    club = relationship("Club", back_populates="members")
