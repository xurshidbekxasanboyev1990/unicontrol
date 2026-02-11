"""
UniControl - Library Service
============================
Business logic for library and book management.

This service handles:
- Book catalog CRUD operations
- Book borrowing and returns
- Book reviews and ratings
- Library statistics

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, timedelta
from app.config import now_tashkent, today_tashkent
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.library import (
    Book, BookBorrow, BookReview,
    BookCategory, BookStatus, BorrowStatus
)
from app.schemas.library import (
    BookCreate, BookUpdate, BookResponse,
    BookBorrowCreate, BookBorrowUpdate, BookBorrowResponse,
    BookReviewCreate, BookReviewUpdate, BookReviewResponse,
    LibraryStats, UserBorrowStats, CategoryStats
)


# Default borrow period in days
DEFAULT_BORROW_DAYS = 14

# Late fee per day (in so'm)
LATE_FEE_PER_DAY = 1000


class LibraryService:
    """
    Service class for library management operations.
    
    Provides methods for:
    - Book catalog management
    - Borrowing operations
    - Reviews and ratings
    - Statistics
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize library service.
        
        Args:
            db: AsyncSession database connection
        """
        self.db = db
    
    # ==================== BOOK OPERATIONS ====================
    
    async def create_book(self, data: BookCreate) -> Book:
        """
        Create a new book.
        
        Args:
            data: Book creation data
            
        Returns:
            Created Book object
        """
        book = Book(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            category=data.category,
            language=data.language,
            description=data.description,
            cover_url=data.cover_url,
            pages=data.pages,
            year=data.year,
            publisher=data.publisher,
            total_copies=data.total_copies,
            available_copies=data.total_copies,
            digital_file_id=data.digital_file_id
        )
        
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        
        return book
    
    async def get_book(self, book_id: int) -> Optional[Book]:
        """
        Get book by ID.
        
        Args:
            book_id: Book ID
            
        Returns:
            Book object or None
        """
        query = select(Book).where(Book.id == book_id).options(
            selectinload(Book.reviews)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Get book by ISBN.
        
        Args:
            isbn: ISBN number
            
        Returns:
            Book object or None
        """
        query = select(Book).where(Book.isbn == isbn)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_books(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[BookCategory] = None,
        search: Optional[str] = None,
        available_only: bool = False,
        sort_by: str = "title"
    ) -> Tuple[List[Book], int]:
        """
        List books with filters and pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            category: Filter by category
            search: Search in title/author
            available_only: Only show available books
            sort_by: Sort field (title, author, year, rating)
            
        Returns:
            Tuple of (books list, total count)
        """
        query = select(Book)
        
        # Apply filters
        if category:
            query = query.where(Book.category == category)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Book.title.ilike(search_pattern),
                    Book.author.ilike(search_pattern),
                    Book.isbn.ilike(search_pattern)
                )
            )
        
        if available_only:
            query = query.where(
                and_(
                    Book.available_copies > 0,
                    Book.status == BookStatus.AVAILABLE
                )
            )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        if sort_by == "author":
            query = query.order_by(Book.author)
        elif sort_by == "year":
            query = query.order_by(Book.year.desc().nullslast())
        elif sort_by == "rating":
            query = query.order_by(Book.rating.desc())
        elif sort_by == "popular":
            query = query.order_by(Book.borrow_count.desc())
        else:
            query = query.order_by(Book.title)
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        books = list(result.scalars().all())
        
        return books, total
    
    async def update_book(self, book_id: int, data: BookUpdate) -> Optional[Book]:
        """
        Update book.
        
        Args:
            book_id: Book ID
            data: Update data
            
        Returns:
            Updated Book or None
        """
        book = await self.get_book(book_id)
        if not book:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle total_copies change
        if 'total_copies' in update_data:
            new_total = update_data['total_copies']
            diff = new_total - book.total_copies
            book.available_copies = max(0, book.available_copies + diff)
        
        for field, value in update_data.items():
            setattr(book, field, value)
        
        book.updated_at = now_tashkent()
        await self.db.commit()
        await self.db.refresh(book)
        
        return book
    
    async def delete_book(self, book_id: int) -> bool:
        """
        Delete book.
        
        Args:
            book_id: Book ID
            
        Returns:
            True if deleted, False otherwise
        """
        book = await self.get_book(book_id)
        if not book:
            return False
        
        # Check for active borrows
        active_borrows = await self.db.execute(
            select(func.count()).select_from(BookBorrow).where(
                and_(
                    BookBorrow.book_id == book_id,
                    BookBorrow.status == BorrowStatus.ACTIVE
                )
            )
        )
        if active_borrows.scalar() > 0:
            raise HTTPException(
                status_code=400,
                detail="Bu kitob hozirda olingan, o'chirib bo'lmaydi"
            )
        
        await self.db.delete(book)
        await self.db.commit()
        
        return True
    
    async def increment_view_count(self, book_id: int) -> None:
        """Increment book view counter."""
        await self.db.execute(
            update(Book).where(Book.id == book_id).values(
                view_count=Book.view_count + 1
            )
        )
        await self.db.commit()
    
    # ==================== BORROW OPERATIONS ====================
    
    async def borrow_book(
        self,
        data: BookBorrowCreate,
        user_id: int
    ) -> BookBorrow:
        """
        Borrow a book.
        
        Args:
            data: Borrow data
            user_id: Borrower user ID
            
        Returns:
            Created BookBorrow record
            
        Raises:
            HTTPException: If book not available
        """
        # Get book
        book = await self.get_book(data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Kitob topilmadi")
        
        # Check availability
        if not book.is_available:
            raise HTTPException(status_code=400, detail="Kitob hozirda mavjud emas")
        
        # Check user's active borrows (limit to 5)
        active_borrows = await self.db.execute(
            select(func.count()).select_from(BookBorrow).where(
                and_(
                    BookBorrow.user_id == user_id,
                    BookBorrow.status == BorrowStatus.ACTIVE
                )
            )
        )
        if active_borrows.scalar() >= 5:
            raise HTTPException(
                status_code=400,
                detail="Siz bir vaqtda 5 tadan ortiq kitob ololmaysiz"
            )
        
        # Create borrow record
        borrow = BookBorrow(
            book_id=data.book_id,
            user_id=user_id,
            student_id=data.student_id,
            borrow_date=today_tashkent(),
            due_date=data.due_date or (today_tashkent() + timedelta(days=DEFAULT_BORROW_DAYS)),
            notes=data.notes
        )
        
        # Update book availability
        book.available_copies -= 1
        book.borrow_count += 1
        if book.available_copies == 0:
            book.status = BookStatus.BORROWED
        
        self.db.add(borrow)
        await self.db.commit()
        await self.db.refresh(borrow)
        
        return borrow
    
    async def return_book(
        self,
        borrow_id: int,
        user_id: int,
        notes: Optional[str] = None
    ) -> BookBorrow:
        """
        Return a borrowed book.
        
        Args:
            borrow_id: Borrow record ID
            user_id: User ID
            notes: Return notes
            
        Returns:
            Updated BookBorrow record
            
        Raises:
            HTTPException: If borrow not found or not active
        """
        # Get borrow record
        borrow = await self.db.get(BookBorrow, borrow_id)
        if not borrow:
            raise HTTPException(status_code=404, detail="Olish yozuvi topilmadi")
        
        if borrow.user_id != user_id:
            raise HTTPException(status_code=403, detail="Bu kitob sizga tegishli emas")
        
        if borrow.status != BorrowStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Bu kitob allaqachon qaytarilgan")
        
        # Calculate late fee
        return_date = today_tashkent()
        if return_date > borrow.due_date:
            days_late = (return_date - borrow.due_date).days
            borrow.late_fee = days_late * LATE_FEE_PER_DAY
        
        # Update borrow record
        borrow.return_date = return_date
        borrow.status = BorrowStatus.RETURNED
        if notes:
            borrow.notes = (borrow.notes or "") + f"\nQaytarish: {notes}"
        
        # Update book availability
        book = await self.get_book(borrow.book_id)
        if book:
            book.available_copies += 1
            if book.status == BookStatus.BORROWED:
                book.status = BookStatus.AVAILABLE
        
        await self.db.commit()
        await self.db.refresh(borrow)
        
        return borrow
    
    async def get_borrow(self, borrow_id: int) -> Optional[BookBorrow]:
        """
        Get borrow record by ID.
        
        Args:
            borrow_id: Borrow ID
            
        Returns:
            BookBorrow or None
        """
        query = select(BookBorrow).where(BookBorrow.id == borrow_id).options(
            selectinload(BookBorrow.book)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_borrows(
        self,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None,
        status: Optional[BorrowStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[BookBorrow], int]:
        """
        List borrow records with filters.
        
        Args:
            user_id: Filter by user
            book_id: Filter by book
            status: Filter by status
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (borrows list, total count)
        """
        query = select(BookBorrow).options(selectinload(BookBorrow.book))
        
        if user_id:
            query = query.where(BookBorrow.user_id == user_id)
        
        if book_id:
            query = query.where(BookBorrow.book_id == book_id)
        
        if status:
            query = query.where(BookBorrow.status == status)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Order and paginate
        query = query.order_by(BookBorrow.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        borrows = list(result.scalars().all())
        
        return borrows, total
    
    async def check_overdue_borrows(self) -> int:
        """
        Check and update overdue borrows.
        
        Returns:
            Number of borrows marked as overdue
        """
        today = today_tashkent()
        
        result = await self.db.execute(
            update(BookBorrow).where(
                and_(
                    BookBorrow.status == BorrowStatus.ACTIVE,
                    BookBorrow.due_date < today
                )
            ).values(status=BorrowStatus.OVERDUE)
        )
        
        await self.db.commit()
        return result.rowcount
    
    # ==================== REVIEW OPERATIONS ====================
    
    async def create_review(
        self,
        data: BookReviewCreate,
        user_id: int
    ) -> BookReview:
        """
        Create a book review.
        
        Args:
            data: Review data
            user_id: Reviewer user ID
            
        Returns:
            Created BookReview
            
        Raises:
            HTTPException: If book not found or already reviewed
        """
        # Check book exists
        book = await self.get_book(data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Kitob topilmadi")
        
        # Check if already reviewed
        existing = await self.db.execute(
            select(BookReview).where(
                and_(
                    BookReview.book_id == data.book_id,
                    BookReview.user_id == user_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Siz bu kitobni allaqachon baholagansiz"
            )
        
        # Create review
        review = BookReview(
            book_id=data.book_id,
            user_id=user_id,
            rating=data.rating,
            review=data.review
        )
        
        self.db.add(review)
        
        # Update book rating
        await self._update_book_rating(data.book_id)
        
        await self.db.commit()
        await self.db.refresh(review)
        
        return review
    
    async def update_review(
        self,
        review_id: int,
        user_id: int,
        data: BookReviewUpdate
    ) -> Optional[BookReview]:
        """
        Update a review.
        
        Args:
            review_id: Review ID
            user_id: User ID (must be owner)
            data: Update data
            
        Returns:
            Updated BookReview or None
        """
        review = await self.db.get(BookReview, review_id)
        if not review or review.user_id != user_id:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)
        
        review.updated_at = now_tashkent()
        
        # Update book rating
        await self._update_book_rating(review.book_id)
        
        await self.db.commit()
        await self.db.refresh(review)
        
        return review
    
    async def delete_review(self, review_id: int, user_id: int) -> bool:
        """
        Delete a review.
        
        Args:
            review_id: Review ID
            user_id: User ID (must be owner)
            
        Returns:
            True if deleted, False otherwise
        """
        review = await self.db.get(BookReview, review_id)
        if not review or review.user_id != user_id:
            return False
        
        book_id = review.book_id
        
        await self.db.delete(review)
        
        # Update book rating
        await self._update_book_rating(book_id)
        
        await self.db.commit()
        
        return True
    
    async def _update_book_rating(self, book_id: int) -> None:
        """
        Recalculate and update book rating.
        
        Args:
            book_id: Book ID
        """
        result = await self.db.execute(
            select(
                func.avg(BookReview.rating),
                func.count(BookReview.id)
            ).where(BookReview.book_id == book_id)
        )
        row = result.one()
        avg_rating = row[0] or 0
        rating_count = row[1] or 0
        
        await self.db.execute(
            update(Book).where(Book.id == book_id).values(
                rating=round(float(avg_rating), 1),
                rating_count=rating_count
            )
        )
    
    async def list_reviews(
        self,
        book_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[BookReview], int]:
        """
        List reviews for a book.
        
        Args:
            book_id: Book ID
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (reviews list, total count)
        """
        query = select(BookReview).where(BookReview.book_id == book_id)
        
        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0
        
        # Paginate
        query = query.order_by(BookReview.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        reviews = list(result.scalars().all())
        
        return reviews, total
    
    # ==================== STATISTICS ====================
    
    async def get_library_stats(self) -> LibraryStats:
        """
        Get overall library statistics.
        
        Returns:
            LibraryStats object
        """
        # Total books and copies
        books_query = select(
            func.count(Book.id),
            func.sum(Book.total_copies),
            func.sum(Book.available_copies)
        )
        books_result = await self.db.execute(books_query)
        books_row = books_result.one()
        
        total_books = books_row[0] or 0
        total_copies = books_row[1] or 0
        available_copies = books_row[2] or 0
        
        # Borrowed and overdue
        borrowed_query = select(func.count()).select_from(BookBorrow).where(
            BookBorrow.status == BorrowStatus.ACTIVE
        )
        borrowed = (await self.db.execute(borrowed_query)).scalar() or 0
        
        overdue_query = select(func.count()).select_from(BookBorrow).where(
            BookBorrow.status == BorrowStatus.OVERDUE
        )
        overdue = (await self.db.execute(overdue_query)).scalar() or 0
        
        total_borrows_query = select(func.count()).select_from(BookBorrow)
        total_borrows = (await self.db.execute(total_borrows_query)).scalar() or 0
        
        # Books by category
        category_query = select(
            Book.category, func.count()
        ).group_by(Book.category)
        category_result = await self.db.execute(category_query)
        books_by_category = {
            str(row[0].value): row[1] for row in category_result.all()
        }
        
        # Popular books
        popular_query = select(Book).order_by(Book.borrow_count.desc()).limit(5)
        popular_result = await self.db.execute(popular_query)
        popular_books = list(popular_result.scalars().all())
        
        # Recent additions
        recent_query = select(Book).order_by(Book.created_at.desc()).limit(5)
        recent_result = await self.db.execute(recent_query)
        recent_books = list(recent_result.scalars().all())
        
        return LibraryStats(
            total_books=total_books,
            total_copies=total_copies,
            available_books=available_copies,
            borrowed_books=borrowed,
            overdue_books=overdue,
            total_borrows=total_borrows,
            books_by_category=books_by_category,
            popular_books=[BookResponse.model_validate(b) for b in popular_books],
            recent_additions=[BookResponse.model_validate(b) for b in recent_books]
        )
    
    async def get_user_borrow_stats(self, user_id: int) -> UserBorrowStats:
        """
        Get user's borrowing statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            UserBorrowStats object
        """
        # Get all borrows for user
        borrows_query = select(BookBorrow).where(
            BookBorrow.user_id == user_id
        ).options(selectinload(BookBorrow.book))
        
        borrows_result = await self.db.execute(borrows_query)
        all_borrows = list(borrows_result.scalars().all())
        
        # Calculate stats
        total = len(all_borrows)
        active = [b for b in all_borrows if b.status == BorrowStatus.ACTIVE]
        returned_on_time = len([
            b for b in all_borrows 
            if b.status == BorrowStatus.RETURNED and 
            b.return_date and b.return_date <= b.due_date
        ])
        returned_late = len([
            b for b in all_borrows
            if b.status == BorrowStatus.RETURNED and
            b.return_date and b.return_date > b.due_date
        ])
        overdue = [b for b in all_borrows if b.status == BorrowStatus.OVERDUE]
        
        return UserBorrowStats(
            total_borrowed=total,
            currently_borrowed=len(active),
            returned_on_time=returned_on_time,
            returned_late=returned_late,
            overdue_now=len(overdue),
            active_borrows=[BookBorrowResponse.model_validate(b) for b in active],
            borrow_history=[BookBorrowResponse.model_validate(b) for b in all_borrows[:20]]
        )
    
    async def get_similar_books(self, book_id: int, limit: int = 5) -> List[Book]:
        """
        Get similar books based on category and author.
        
        Args:
            book_id: Book ID
            limit: Number of similar books to return
            
        Returns:
            List of similar Book objects
        """
        book = await self.get_book(book_id)
        if not book:
            return []
        
        query = select(Book).where(
            and_(
                Book.id != book_id,
                or_(
                    Book.category == book.category,
                    Book.author == book.author
                )
            )
        ).order_by(Book.rating.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())