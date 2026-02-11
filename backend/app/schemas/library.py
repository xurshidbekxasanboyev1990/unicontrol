"""
UniControl - Library Schemas
============================
Pydantic schemas for library and book operations.

These schemas handle:
- Book catalog management
- Book borrowing operations
- Book reviews and ratings
- Library statistics

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.library import BookCategory, BookLanguage, BookStatus, BorrowStatus
from app.config import today_tashkent


# ==================== BOOK SCHEMAS ====================

class BookBase(BaseModel):
    """
    Base book schema with common fields.
    """
    title: str = Field(..., min_length=1, max_length=500, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Author name(s)")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN number")
    category: BookCategory = Field(BookCategory.BOSHQA, description="Book category")
    language: BookLanguage = Field(BookLanguage.UZ, description="Book language")
    description: Optional[str] = Field(None, description="Book description")
    cover_url: Optional[str] = Field(None, max_length=500, description="Cover image URL")
    pages: Optional[int] = Field(None, ge=1, description="Number of pages")
    year: Optional[int] = Field(None, ge=1800, le=2100, description="Publication year")
    publisher: Optional[str] = Field(None, max_length=255, description="Publisher name")


class BookCreate(BookBase):
    """
    Schema for book creation.
    """
    total_copies: int = Field(1, ge=1, description="Total copies in library")
    digital_file_id: Optional[int] = Field(None, description="E-book file reference")
    
    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    """
    Schema for book update.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    category: Optional[BookCategory] = None
    language: Optional[BookLanguage] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    pages: Optional[int] = Field(None, ge=1)
    year: Optional[int] = Field(None, ge=1800, le=2100)
    publisher: Optional[str] = None
    status: Optional[BookStatus] = None
    total_copies: Optional[int] = Field(None, ge=0)
    digital_file_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class BookResponse(BaseModel):
    """
    Schema for book response.
    """
    id: int
    title: str
    author: str
    isbn: Optional[str]
    category: BookCategory
    language: BookLanguage
    description: Optional[str]
    cover_url: Optional[str]
    pages: Optional[int]
    year: Optional[int]
    publisher: Optional[str]
    status: BookStatus
    total_copies: int
    available_copies: int
    rating: float
    rating_count: int
    borrow_count: int
    view_count: int
    is_available: bool
    digital_file_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BookListResponse(BaseModel):
    """
    Paginated book list response.
    """
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(from_attributes=True)


class BookDetailResponse(BookResponse):
    """
    Detailed book response with reviews.
    """
    reviews: List["BookReviewResponse"] = []
    similar_books: List["BookResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# ==================== BORROW SCHEMAS ====================

class BookBorrowCreate(BaseModel):
    """
    Schema for borrowing a book.
    """
    book_id: int = Field(..., description="Book ID to borrow")
    student_id: Optional[int] = Field(None, description="Student ID if applicable")
    due_date: date = Field(..., description="Return due date")
    notes: Optional[str] = Field(None, max_length=500, description="Borrow notes")
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v < today_tashkent():
            raise ValueError("Qaytarish sanasi bugungi kundan oldin bo'lishi mumkin emas")
        return v
    
    model_config = ConfigDict(from_attributes=True)


class BookBorrowUpdate(BaseModel):
    """
    Schema for updating borrow record.
    """
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[BorrowStatus] = None
    
    model_config = ConfigDict(from_attributes=True)


class BookReturnRequest(BaseModel):
    """
    Schema for returning a book.
    """
    borrow_id: int = Field(..., description="Borrow record ID")
    notes: Optional[str] = Field(None, max_length=500, description="Return notes")
    
    model_config = ConfigDict(from_attributes=True)


class BookBorrowResponse(BaseModel):
    """
    Schema for borrow record response.
    """
    id: int
    book_id: int
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    user_id: int
    student_id: Optional[int]
    borrow_date: date
    due_date: date
    return_date: Optional[date]
    status: BorrowStatus
    notes: Optional[str]
    late_fee: float
    is_overdue: bool
    days_overdue: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BookBorrowListResponse(BaseModel):
    """
    Paginated borrow list response.
    """
    items: List[BookBorrowResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== REVIEW SCHEMAS ====================

class BookReviewCreate(BaseModel):
    """
    Schema for creating a book review.
    """
    book_id: int = Field(..., description="Book ID")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    review: Optional[str] = Field(None, max_length=2000, description="Review text")
    
    model_config = ConfigDict(from_attributes=True)


class BookReviewUpdate(BaseModel):
    """
    Schema for updating a review.
    """
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BookReviewResponse(BaseModel):
    """
    Schema for review response.
    """
    id: int
    book_id: int
    user_id: int
    user_name: Optional[str] = None
    rating: int
    review: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== LIBRARY STATISTICS ====================

class LibraryStats(BaseModel):
    """
    Library statistics schema.
    """
    total_books: int
    total_copies: int
    available_books: int
    borrowed_books: int
    overdue_books: int
    total_borrows: int
    books_by_category: dict
    popular_books: List[BookResponse]
    recent_additions: List[BookResponse]
    
    model_config = ConfigDict(from_attributes=True)


class UserBorrowStats(BaseModel):
    """
    User's borrowing statistics.
    """
    total_borrowed: int
    currently_borrowed: int
    returned_on_time: int
    returned_late: int
    overdue_now: int
    active_borrows: List[BookBorrowResponse]
    borrow_history: List[BookBorrowResponse]
    
    model_config = ConfigDict(from_attributes=True)


class CategoryStats(BaseModel):
    """
    Statistics for a book category.
    """
    category: BookCategory
    category_name: str
    total_books: int
    total_copies: int
    available_copies: int
    borrow_count: int
    popular_books: List[BookResponse]
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references
BookDetailResponse.model_rebuild()
