"""
UniControl Backend - Database Module
=====================================
Async SQLAlchemy database connection and session management.
Supports PostgreSQL with asyncpg driver.

Author: UniControl Team
Version: 1.0.0
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from app.config import settings


# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    All models should inherit from this class.
    """
    metadata = metadata


# Create async engine - SQLite doesn't support pool settings
def _create_engine():
    """Create engine with appropriate settings for database type."""
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    
    if is_sqlite:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            connect_args={"check_same_thread": False}
        )
    else:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

engine: AsyncEngine = _create_engine()

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Automatically handles commit/rollback and closes session.
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database - create all tables.
    Should be called on application startup in development.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import (
            user, student, group, attendance, 
            schedule, notification, report
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    await engine.dispose()
