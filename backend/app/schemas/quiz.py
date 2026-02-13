"""
UniControl - Quiz Schemas
==========================
Pydantic schemas for quiz/flashcard endpoints.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============ QuizCard Schemas ============

class QuizCardBase(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    answer_type: str = Field(default="text")  # text, multiple_choice, true_false
    options: Optional[List[str]] = None
    correct_option: Optional[int] = None
    hint: Optional[str] = None
    order: int = 0


class QuizCardCreate(QuizCardBase):
    pass


class QuizCardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    answer_type: Optional[str] = None
    options: Optional[List[str]] = None
    correct_option: Optional[int] = None
    hint: Optional[str] = None
    order: Optional[int] = None


class QuizCardResponse(QuizCardBase):
    id: int
    quiz_set_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ QuizSet Schemas ============

class QuizSetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = None
    is_public: bool = False
    color: str = "#3b82f6"


class QuizSetCreate(QuizSetBase):
    cards: Optional[List[QuizCardCreate]] = []


class QuizSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    is_public: Optional[bool] = None
    color: Optional[str] = None


class QuizSetResponse(QuizSetBase):
    id: int
    creator_id: int
    group_id: Optional[int] = None
    cards_count: int = 0
    play_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    group_name: Optional[str] = None
    cards: Optional[List[QuizCardResponse]] = []

    class Config:
        from_attributes = True


class QuizSetListResponse(BaseModel):
    items: List[QuizSetResponse]
    total: int
    page: int
    page_size: int


# ============ QuizResult Schemas ============

class QuizResultCreate(BaseModel):
    quiz_set_id: int
    total_questions: int
    correct_answers: int
    score_percentage: int = 0
    time_spent_seconds: int = 0
    mode: str = "quiz"


class QuizResultResponse(BaseModel):
    id: int
    quiz_set_id: int
    user_id: int
    total_questions: int
    correct_answers: int
    score_percentage: int
    time_spent_seconds: int
    mode: str
    completed_at: Optional[datetime] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
