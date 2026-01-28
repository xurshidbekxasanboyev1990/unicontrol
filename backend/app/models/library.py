"""
UniControl - Library/Book Model
================================
Database model for library and book management.

This model handles:
- Book catalog management
- Book categories and authors
- Book borrowing and returns
- Digital book access

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Text, Boolean, Date, Float, Enum as SQLEnum
)
from sqlalchemy.orm import relationship

from app.database import Base


class BookCategory(str, Enum):
    """
    Book category enumeration.
    Used to categorize books by subject/genre.
    """
    DARSLIK = "darslik"        # Textbooks
    ILMIY = "ilmiy"            # Scientific
    BADIIY = "badiiy"          # Fiction/Literature
    TEXNIK = "texnik"          # Technical
    DINIY = "diniy"            # Religious
    TARIX = "tarix"            # History
    FALSAFA = "falsafa"        # Philosophy
    PSIXOLOGIYA = "psixologiya"  # Psychology
    IQTISOD = "iqtisod"        # Economics
    HUQUQ = "huquq"            # Law
    TIBBIYOT = "tibbiyot"      # Medicine
    BOSHQA = "boshqa"          # Other


class BookLanguage(str, Enum):
    """
    Book language enumeration.
    """
    UZ = "uz"      # O'zbekcha
    RU = "ru"      # Ruscha
    EN = "en"      # Inglizcha
    AR = "ar"      # Arabcha
    OTHER = "other"  # Boshqa


class BookStatus(str, Enum):
    """
    Book availability status.
    """
    AVAILABLE = "available"      # Mavjud
    BORROWED = "borrowed"        # Olingan
    RESERVED = "reserved"        # Band qilingan
    MAINTENANCE = "maintenance"  # Ta'mirda
    LOST = "lost"               # Yo'qolgan


class BorrowStatus(str, Enum):
    """
    Borrow record status.
    """
    ACTIVE = "active"        # Hozirda olingan
    RETURNED = "returned"    # Qaytarilgan
    OVERDUE = "overdue"      # Muddati o'tgan
    LOST = "lost"           # Yo'qotilgan


class Book(Base):
    """
    Book database model.
    
    Stores library book information including:
    - Book details (title, author, ISBN)
    - Category and language
    - Physical details (pages, year)
    - Availability status
    - Digital file reference (if e-book)
    
    Attributes:
        id: Primary key
        title: Book title
        author: Author name(s)
        isbn: ISBN number (optional)
        category: Book category
        language: Book language
        description: Book description/summary
        cover_url: Cover image URL
        pages: Number of pages
        year: Publication year
        publisher: Publisher name
        status: Availability status
        total_copies: Total copies in library
        available_copies: Currently available copies
        rating: Average rating (1-5)
        rating_count: Number of ratings
        digital_file_id: Reference to digital file (e-book)
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Book information
    title = Column(String(500), nullable=False, index=True, comment="Book title")
    author = Column(String(255), nullable=False, index=True, comment="Author name(s)")
    isbn = Column(String(20), nullable=True, unique=True, comment="ISBN number")
    
    # Classification
    category = Column(
        SQLEnum(BookCategory), 
        nullable=False, 
        default=BookCategory.BOSHQA,
        index=True,
        comment="Book category"
    )
    language = Column(
        SQLEnum(BookLanguage), 
        nullable=False, 
        default=BookLanguage.UZ,
        comment="Book language"
    )
    
    # Details
    description = Column(Text, nullable=True, comment="Book description/summary")
    cover_url = Column(String(500), nullable=True, comment="Cover image URL")
    pages = Column(Integer, nullable=True, comment="Number of pages")
    year = Column(Integer, nullable=True, comment="Publication year")
    publisher = Column(String(255), nullable=True, comment="Publisher name")
    
    # Availability
    status = Column(
        SQLEnum(BookStatus), 
        nullable=False, 
        default=BookStatus.AVAILABLE,
        comment="Current status"
    )
    total_copies = Column(Integer, default=1, comment="Total copies in library")
    available_copies = Column(Integer, default=1, comment="Currently available")
    
    # Ratings
    rating = Column(Float, default=0.0, comment="Average rating (1-5)")
    rating_count = Column(Integer, default=0, comment="Number of ratings")
    
    # Digital book reference
    digital_file_id = Column(
        Integer, 
        ForeignKey("files.id", ondelete="SET NULL"), 
        nullable=True,
        comment="E-book file reference"
    )
    
    # Statistics
    borrow_count = Column(Integer, default=0, comment="Total times borrowed")
    view_count = Column(Integer, default=0, comment="View count")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    digital_file = relationship("File", backref="book")
    borrows = relationship("BookBorrow", back_populates="book", cascade="all, delete-orphan")
    reviews = relationship("BookReview", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"
    
    @property
    def is_available(self) -> bool:
        """Check if book is available for borrowing."""
        return self.available_copies > 0 and self.status == BookStatus.AVAILABLE


class BookBorrow(Base):
    """
    Book borrow record model.
    
    Tracks book borrowing history including:
    - Who borrowed the book
    - Borrow and due dates
    - Return date and status
    - Late fees (if applicable)
    
    Attributes:
        id: Primary key
        book_id: Borrowed book reference
        user_id: Borrower user ID
        student_id: Borrower student ID (optional)
        borrow_date: Date borrowed
        due_date: Return due date
        return_date: Actual return date
        status: Borrow status
        notes: Optional notes
        late_fee: Late return fee
    """
    __tablename__ = "book_borrows"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # References
    book_id = Column(
        Integer, 
        ForeignKey("books.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    student_id = Column(
        Integer, 
        ForeignKey("students.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Dates
    borrow_date = Column(Date, nullable=False, default=date.today, comment="Borrow date")
    due_date = Column(Date, nullable=False, comment="Return due date")
    return_date = Column(Date, nullable=True, comment="Actual return date")
    
    # Status
    status = Column(
        SQLEnum(BorrowStatus), 
        nullable=False, 
        default=BorrowStatus.ACTIVE,
        comment="Borrow status"
    )
    
    # Additional info
    notes = Column(Text, nullable=True, comment="Notes about borrow")
    late_fee = Column(Float, default=0.0, comment="Late return fee")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="borrows")
    user = relationship("User", backref="book_borrows")
    student = relationship("Student", backref="book_borrows")
    
    def __repr__(self):
        return f"<BookBorrow(id={self.id}, book_id={self.book_id}, user_id={self.user_id})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if borrow is overdue."""
        if self.return_date:
            return False
        return date.today() > self.due_date
    
    @property
    def days_overdue(self) -> int:
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days


class BookReview(Base):
    """
    Book review model.
    
    Stores user reviews and ratings for books.
    
    Attributes:
        id: Primary key
        book_id: Reviewed book
        user_id: Reviewer
        rating: Rating (1-5)
        review: Review text
        created_at: Review date
    """
    __tablename__ = "book_reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # References
    book_id = Column(
        Integer, 
        ForeignKey("books.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Review content
    rating = Column(Integer, nullable=False, comment="Rating 1-5")
    review = Column(Text, nullable=True, comment="Review text")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", backref="book_reviews")
    
    def __repr__(self):
        return f"<BookReview(id={self.id}, book_id={self.book_id}, rating={self.rating})>"
