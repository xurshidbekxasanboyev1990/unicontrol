"""
UniControl - Library Routes
===========================
Library and book management API endpoints.

This module provides:
- Book catalog CRUD operations
- Book borrowing and returns
- Book reviews and ratings
- Library statistics
- User borrow history

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.library_service import LibraryService
from app.schemas.library import (
    BookCreate, BookUpdate, BookResponse, BookListResponse, BookDetailResponse,
    BookBorrowCreate, BookBorrowUpdate, BookBorrowResponse, BookBorrowListResponse,
    BookReturnRequest, BookReviewCreate, BookReviewUpdate, BookReviewResponse,
    LibraryStats, UserBorrowStats, CategoryStats
)
from app.models.library import BookCategory, BookStatus, BorrowStatus
from app.core.dependencies import get_current_active_user, require_admin, require_leader
from app.models.user import User

router = APIRouter()


# ==================== BOOK ENDPOINTS ====================

@router.get("/books", response_model=BookListResponse)
async def list_books(
    page: int = Query(1, ge=1, description="Sahifa raqami"),
    page_size: int = Query(20, ge=1, le=100, description="Sahifadagi kitoblar soni"),
    category: Optional[BookCategory] = Query(None, description="Kategoriya filtri"),
    search: Optional[str] = Query(None, max_length=100, description="Qidiruv (nomi, muallif)"),
    available_only: bool = Query(False, description="Faqat mavjud kitoblar"),
    sort_by: str = Query("title", description="Saralash: title, author, year, rating, popular"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List books with filters and pagination.
    
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (max 100)
    - **category**: Filter by book category
    - **search**: Search in title, author, ISBN
    - **available_only**: Show only available books
    - **sort_by**: Sort by field (title, author, year, rating, popular)
    
    Returns paginated list of books.
    """
    service = LibraryService(db)
    
    books, total = await service.list_books(
        page=page,
        page_size=page_size,
        category=category,
        search=search,
        available_only=available_only,
        sort_by=sort_by
    )
    
    return BookListResponse(
        items=[BookResponse.model_validate(b) for b in books],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/books/{book_id}", response_model=BookDetailResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed book information by ID.
    
    Returns book details including reviews and similar books.
    Also increments view counter.
    """
    service = LibraryService(db)
    book = await service.get_book(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi")
    
    # Increment view count
    await service.increment_view_count(book_id)
    
    # Get similar books
    similar = await service.get_similar_books(book_id)
    
    # Build response
    response = BookDetailResponse.model_validate(book)
    response.similar_books = [BookResponse.model_validate(b) for b in similar]
    response.reviews = [BookReviewResponse.model_validate(r) for r in (book.reviews or [])]
    
    return response


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new book (Admin only).
    
    - **title**: Book title (required)
    - **author**: Author name (required)
    - **isbn**: ISBN number (optional, unique)
    - **category**: Book category
    - **language**: Book language
    - **description**: Book description
    - **cover_url**: Cover image URL
    - **pages**: Number of pages
    - **year**: Publication year
    - **publisher**: Publisher name
    - **total_copies**: Number of copies in library
    - **digital_file_id**: E-book file reference
    """
    service = LibraryService(db)
    
    # Check ISBN uniqueness
    if data.isbn:
        existing = await service.get_book_by_isbn(data.isbn)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bu ISBN ({data.isbn}) bilan kitob allaqachon mavjud"
            )
    
    book = await service.create_book(data)
    return BookResponse.model_validate(book)


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update book information (Admin only).
    
    All fields are optional - only provided fields will be updated.
    """
    service = LibraryService(db)
    book = await service.update_book(book_id, data)
    
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi")
    
    return BookResponse.model_validate(book)


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a book (Admin only).
    
    Cannot delete books that are currently borrowed.
    """
    service = LibraryService(db)
    deleted = await service.delete_book(book_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Kitob topilmadi")
    
    return None


# ==================== BORROW ENDPOINTS ====================

@router.post("/borrow", response_model=BookBorrowResponse, status_code=status.HTTP_201_CREATED)
async def borrow_book(
    data: BookBorrowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Borrow a book.
    
    - **book_id**: Book ID to borrow (required)
    - **student_id**: Student ID if applicable (optional)
    - **due_date**: Return due date (required, must be future)
    - **notes**: Borrow notes (optional)
    
    Rules:
    - Maximum 5 active borrows per user
    - Book must be available
    - Due date must be in the future
    """
    service = LibraryService(db)
    borrow = await service.borrow_book(data, current_user.id)
    
    return BookBorrowResponse(
        id=borrow.id,
        book_id=borrow.book_id,
        book_title=borrow.book.title if borrow.book else None,
        book_author=borrow.book.author if borrow.book else None,
        user_id=borrow.user_id,
        student_id=borrow.student_id,
        borrow_date=borrow.borrow_date,
        due_date=borrow.due_date,
        return_date=borrow.return_date,
        status=borrow.status,
        notes=borrow.notes,
        late_fee=borrow.late_fee,
        is_overdue=borrow.is_overdue,
        days_overdue=borrow.days_overdue,
        created_at=borrow.created_at
    )


@router.post("/return", response_model=BookBorrowResponse)
async def return_book(
    data: BookReturnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Return a borrowed book.
    
    - **borrow_id**: Borrow record ID (required)
    - **notes**: Return notes (optional)
    
    Late fees will be calculated automatically if overdue.
    """
    service = LibraryService(db)
    borrow = await service.return_book(
        borrow_id=data.borrow_id,
        user_id=current_user.id,
        notes=data.notes
    )
    
    return BookBorrowResponse(
        id=borrow.id,
        book_id=borrow.book_id,
        book_title=borrow.book.title if borrow.book else None,
        book_author=borrow.book.author if borrow.book else None,
        user_id=borrow.user_id,
        student_id=borrow.student_id,
        borrow_date=borrow.borrow_date,
        due_date=borrow.due_date,
        return_date=borrow.return_date,
        status=borrow.status,
        notes=borrow.notes,
        late_fee=borrow.late_fee,
        is_overdue=False,
        days_overdue=0,
        created_at=borrow.created_at
    )


@router.get("/borrows", response_model=BookBorrowListResponse)
async def list_borrows(
    book_id: Optional[int] = Query(None, description="Kitob ID filtri"),
    borrow_status: Optional[BorrowStatus] = Query(None, description="Status filtri"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's borrow records.
    
    - **book_id**: Filter by specific book
    - **status**: Filter by borrow status (active, returned, overdue)
    - **page**: Page number
    - **page_size**: Items per page
    """
    service = LibraryService(db)
    
    borrows, total = await service.list_borrows(
        user_id=current_user.id,
        book_id=book_id,
        status=borrow_status,
        page=page,
        page_size=page_size
    )
    
    items = []
    for b in borrows:
        items.append(BookBorrowResponse(
            id=b.id,
            book_id=b.book_id,
            book_title=b.book.title if b.book else None,
            book_author=b.book.author if b.book else None,
            user_id=b.user_id,
            student_id=b.student_id,
            borrow_date=b.borrow_date,
            due_date=b.due_date,
            return_date=b.return_date,
            status=b.status,
            notes=b.notes,
            late_fee=b.late_fee,
            is_overdue=b.is_overdue,
            days_overdue=b.days_overdue,
            created_at=b.created_at
        ))
    
    return BookBorrowListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/borrows/all", response_model=BookBorrowListResponse)
async def list_all_borrows(
    user_id: Optional[int] = Query(None, description="Foydalanuvchi ID"),
    book_id: Optional[int] = Query(None, description="Kitob ID"),
    borrow_status: Optional[BorrowStatus] = Query(None, description="Status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    List all borrow records (Leader/Admin only).
    
    Can filter by user, book, and status.
    """
    service = LibraryService(db)
    
    borrows, total = await service.list_borrows(
        user_id=user_id,
        book_id=book_id,
        status=borrow_status,
        page=page,
        page_size=page_size
    )
    
    items = []
    for b in borrows:
        items.append(BookBorrowResponse(
            id=b.id,
            book_id=b.book_id,
            book_title=b.book.title if b.book else None,
            book_author=b.book.author if b.book else None,
            user_id=b.user_id,
            student_id=b.student_id,
            borrow_date=b.borrow_date,
            due_date=b.due_date,
            return_date=b.return_date,
            status=b.status,
            notes=b.notes,
            late_fee=b.late_fee,
            is_overdue=b.is_overdue,
            days_overdue=b.days_overdue,
            created_at=b.created_at
        ))
    
    return BookBorrowListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ==================== REVIEW ENDPOINTS ====================

@router.post("/books/{book_id}/reviews", response_model=BookReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    data: BookReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a book review.
    
    - **rating**: Rating from 1 to 5 (required)
    - **review**: Review text (optional)
    
    Each user can only review a book once.
    """
    # Ensure book_id matches
    data.book_id = book_id
    
    service = LibraryService(db)
    review = await service.create_review(data, current_user.id)
    
    return BookReviewResponse(
        id=review.id,
        book_id=review.book_id,
        user_id=review.user_id,
        user_name=current_user.full_name or current_user.login,
        rating=review.rating,
        review=review.review,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.get("/books/{book_id}/reviews")
async def list_reviews(
    book_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List reviews for a book.
    """
    service = LibraryService(db)
    reviews, total = await service.list_reviews(book_id, page, page_size)
    
    return {
        "items": [BookReviewResponse.model_validate(r) for r in reviews],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/reviews/{review_id}", response_model=BookReviewResponse)
async def update_review(
    review_id: int,
    data: BookReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update own review.
    """
    service = LibraryService(db)
    review = await service.update_review(review_id, current_user.id, data)
    
    if not review:
        raise HTTPException(status_code=404, detail="Sharh topilmadi yoki ruxsat yo'q")
    
    return BookReviewResponse.model_validate(review)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete own review.
    """
    service = LibraryService(db)
    deleted = await service.delete_review(review_id, current_user.id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Sharh topilmadi yoki ruxsat yo'q")
    
    return None


# ==================== STATISTICS ENDPOINTS ====================

@router.get("/stats", response_model=LibraryStats)
async def get_library_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get library statistics.
    
    Returns:
    - Total books and copies
    - Available and borrowed counts
    - Books by category
    - Popular books
    - Recent additions
    """
    service = LibraryService(db)
    return await service.get_library_stats()


@router.get("/my-stats", response_model=UserBorrowStats)
async def get_my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's borrowing statistics.
    
    Returns:
    - Total borrowed count
    - Currently borrowed
    - Return statistics
    - Active borrows list
    - Borrow history
    """
    service = LibraryService(db)
    return await service.get_user_borrow_stats(current_user.id)


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all book categories with Uzbek names.
    """
    category_names = {
        "darslik": "Darsliklar",
        "ilmiy": "Ilmiy adabiyotlar",
        "badiiy": "Badiiy adabiyotlar",
        "texnik": "Texnik adabiyotlar",
        "diniy": "Diniy adabiyotlar",
        "tarix": "Tarix",
        "falsafa": "Falsafa",
        "psixologiya": "Psixologiya",
        "iqtisod": "Iqtisodiyot",
        "huquq": "Huquqshunoslik",
        "tibbiyot": "Tibbiyot",
        "boshqa": "Boshqa"
    }
    
    return [
        {"id": cat.value, "name": category_names.get(cat.value, cat.value)}
        for cat in BookCategory
    ]


# ==================== ADMIN ENDPOINTS ====================

@router.post("/check-overdue")
async def check_overdue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Check and update overdue borrows (Admin only).
    
    Marks all borrows past due date as overdue.
    Should be run periodically (daily).
    """
    service = LibraryService(db)
    count = await service.check_overdue_borrows()
    
    return {
        "message": f"{count} ta qarz muddati o'tgan deb belgilandi",
        "overdue_count": count
    }
