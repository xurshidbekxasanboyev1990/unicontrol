"""
UniControl - Quiz Models (Quizlet-style)
=========================================
FlashCard sets with questions/answers, group-scoped sharing.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class QuizSet(Base):
    """A collection of flashcards/quiz questions created by a student or leader."""
    __tablename__ = "quiz_sets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(255), nullable=True)  # Fan nomi (ixtiyoriy)
    
    # Creator info
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    
    # Visibility
    is_public = Column(Boolean, default=False)  # False = faqat guruh ko'radi
    
    # Stats
    cards_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)  # Necha marta o'ynalgan
    
    # Colors/theme
    color = Column(String(20), default="#3b82f6")  # Card rang
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = relationship("User", backref="quiz_sets", lazy="selectin")
    group = relationship("Group", backref="quiz_sets", lazy="selectin")
    cards = relationship("QuizCard", back_populates="quiz_set", cascade="all, delete-orphan", order_by="QuizCard.order", lazy="selectin")
    results = relationship("QuizResult", back_populates="quiz_set", cascade="all, delete-orphan", lazy="noload")


class QuizCard(Base):
    """A single flashcard/question in a quiz set."""
    __tablename__ = "quiz_cards"

    id = Column(Integer, primary_key=True, index=True)
    quiz_set_id = Column(Integer, ForeignKey("quiz_sets.id", ondelete="CASCADE"), nullable=False)
    
    # Question
    question = Column(Text, nullable=False)
    
    # Answer type: 'text', 'multiple_choice', 'true_false'
    answer_type = Column(String(20), default="text")
    
    # Correct answer (for flashcard mode / text answer)
    answer = Column(Text, nullable=False)
    
    # Multiple choice options (JSON array: ["A variant", "B variant", ...])
    options = Column(JSON, nullable=True)
    
    # Correct option index for multiple choice (0-based)
    correct_option = Column(Integer, nullable=True)
    
    # Hint (optional)
    hint = Column(Text, nullable=True)
    
    # Order in set
    order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    quiz_set = relationship("QuizSet", back_populates="cards")


class QuizResult(Base):
    """Track quiz results for a user."""
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    quiz_set_id = Column(Integer, ForeignKey("quiz_sets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Results
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Integer, default=0)  # 0-100
    time_spent_seconds = Column(Integer, default=0)
    
    # Mode: 'flashcard', 'quiz', 'test'
    mode = Column(String(20), default="quiz")
    
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    quiz_set = relationship("QuizSet", back_populates="results")
    user = relationship("User", backref="quiz_results", lazy="selectin")
