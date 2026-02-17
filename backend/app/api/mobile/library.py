"""
UniControl - Mobile Library Routes
===================================
Mobile endpoints for library/books.
"""

from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User
from app.models.library import Book, BookCategory, BookBorrow, BorrowStatus, BookStatus
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_books(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get books list with search and category filter."""
    query = select(Book)

    if search:
        query = query.where(
            Book.title.ilike(f"%{search}%") |
            Book.author.ilike(f"%{search}%")
        )
    if category:
        try:
            cat = BookCategory(category)
            query = query.where(Book.category == cat)
        except ValueError:
            pass

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Items
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(desc(Book.created_at)).offset(offset).limit(page_size))
    books = result.scalars().all()

    return {
        "items": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "category": b.category.value if b.category else None,
                "language": b.language.value if b.language else None,
                "isbn": b.isbn,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies,
                "cover_url": b.cover_url,
                "description": b.description,
                "pages": b.pages,
                "year": b.year,
                "publisher": b.publisher,
                "rating": float(b.rating) if b.rating else 0.0,
                "view_count": b.view_count or 0,
                "status": b.status.value if b.status else None,
            }
            for b in books
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_active_user),
):
    """Get book categories."""
    category_names = {
        "darslik": "Darslik",
        "ilmiy": "Ilmiy adabiyot",
        "badiiy": "Badiiy adabiyot",
        "texnik": "Texnik adabiyot",
        "diniy": "Diniy adabiyot",
        "tarixiy": "Tarixiy adabiyot",
        "huquqiy": "Huquqiy adabiyot",
        "tibbiyot": "Tibbiyot",
        "iqtisodiyot": "Iqtisodiyot",
        "pedagogika": "Pedagogika",
        "psixologiya": "Psixologiya",
        "boshqa": "Boshqa",
    }
    return [
        {"value": c.value, "name": category_names.get(c.value, c.value)}
        for c in BookCategory
    ]


@router.get("/my-borrows")
async def get_my_borrows(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's borrowed books."""
    query = select(BookBorrow).where(BookBorrow.user_id == current_user.id)

    if status:
        try:
            st = BorrowStatus(status)
            query = query.where(BookBorrow.status == st)
        except ValueError:
            pass

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(desc(BookBorrow.borrow_date)).offset(offset).limit(page_size)
    )
    borrows = result.scalars().all()

    items = []
    for br in borrows:
        book_res = await db.execute(select(Book).where(Book.id == br.book_id))
        book = book_res.scalar_one_or_none()
        items.append({
            "id": br.id,
            "book_id": br.book_id,
            "book_title": book.title if book else "Noma'lum",
            "book_author": book.author if book else "",
            "book_cover": book.cover_url if book else None,
            "borrow_date": str(br.borrow_date) if br.borrow_date else None,
            "due_date": str(br.due_date) if br.due_date else None,
            "return_date": str(br.return_date) if br.return_date else None,
            "status": br.status.value if br.status else "active",
            "late_fee": float(br.late_fee) if br.late_fee else 0,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/stats")
async def get_library_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get library statistics for current user."""
    total_books = (await db.execute(select(func.count(Book.id)))).scalar() or 0
    available = (await db.execute(select(func.sum(Book.available_copies)))).scalar() or 0

    my_borrows = (await db.execute(
        select(func.count(BookBorrow.id)).where(
            BookBorrow.user_id == current_user.id
        )
    )).scalar() or 0

    active_borrows = (await db.execute(
        select(func.count(BookBorrow.id)).where(
            BookBorrow.user_id == current_user.id,
            BookBorrow.status == BorrowStatus.ACTIVE,
        )
    )).scalar() or 0

    return {
        "total_books": total_books,
        "available_books": available,
        "my_total_borrows": my_borrows,
        "my_active_borrows": active_borrows,
    }


@router.get("/{book_id}")
async def get_book_detail(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get book details."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi")

    # Increment view count
    book.view_count = (book.view_count or 0) + 1
    db.add(book)
    await db.commit()

    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "category": book.category.value if book.category else None,
        "language": book.language.value if book.language else None,
        "isbn": book.isbn,
        "total_copies": book.total_copies,
        "available_copies": book.available_copies,
        "cover_url": book.cover_url,
        "description": book.description,
        "pages": book.pages,
        "year": book.year,
        "publisher": book.publisher,
        "rating": float(book.rating) if book.rating else 0.0,
        "rating_count": book.rating_count or 0,
        "view_count": book.view_count or 0,
        "status": book.status.value if book.status else None,
    }


@router.post("/{book_id}/borrow")
async def borrow_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Borrow a book."""
    book = (await db.execute(select(Book).where(Book.id == book_id))).scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Kitob mavjud emas")

    # Check active borrows limit
    active = (await db.execute(
        select(func.count(BookBorrow.id)).where(
            BookBorrow.user_id == current_user.id,
            BookBorrow.status == BorrowStatus.ACTIVE,
        )
    )).scalar() or 0

    if active >= 5:
        raise HTTPException(status_code=400, detail="Maksimal 5 ta kitob olish mumkin")

    # Check if already borrowed this book
    existing = (await db.execute(
        select(BookBorrow).where(
            BookBorrow.user_id == current_user.id,
            BookBorrow.book_id == book_id,
            BookBorrow.status == BorrowStatus.ACTIVE,
        )
    )).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Bu kitob allaqachon olingan")

    borrow = BookBorrow(
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=date.today(),
        due_date=date.today() + timedelta(days=14),
        status=BorrowStatus.ACTIVE,
    )
    db.add(borrow)
    book.available_copies -= 1
    db.add(book)
    await db.commit()

    return {"success": True, "message": "Kitob muvaffaqiyatli olindi", "due_date": str(borrow.due_date)}
