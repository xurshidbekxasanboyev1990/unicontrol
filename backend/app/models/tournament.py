"""
Tournament (Turnir) Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import TASHKENT_TZ
from app.database import Base


class Tournament(Base):
    """Turnir modeli"""
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default='sport')  # sport, intellektual, ijod
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    registration_deadline = Column(Date, nullable=True)
    location = Column(String(200), nullable=True)
    max_participants = Column(Integer, default=100)
    prize = Column(String(500), nullable=True)  # Mukofot
    rules = Column(Text, nullable=True)  # Qoidalar
    status = Column(String(50), default='upcoming')  # upcoming, active, completed, cancelled
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), onupdate=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    registrations = relationship("TournamentRegistration", back_populates="tournament", cascade="all, delete-orphan")


class TournamentRegistration(Base):
    """Turnirga ro'yxatdan o'tish"""
    __tablename__ = "tournament_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    status = Column(String(50), default='registered')  # registered, confirmed, cancelled
    position = Column(Integer, nullable=True)  # Yakuniy o'rin
    score = Column(Integer, nullable=True)  # Ball
    
    # Relationships
    tournament = relationship("Tournament", back_populates="registrations")
