"""
UniControl Backend - Database Module
=====================================
Async SQLAlchemy database connection and session management.
Supports PostgreSQL with asyncpg driver.

Author: UniControl Team
Version: 1.0.0
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
import sqlalchemy as sa

from app.config import settings

logger = logging.getLogger(__name__)


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
            schedule, notification, report,
            mutoola, activity_log, file,
            library, canteen, club, subject, tournament,
            system_settings
        )
        await conn.run_sync(Base.metadata.create_all)
    
    # Add missing columns for existing tables (safe migration)
    async with engine.begin() as conn:
        # Add telegram_notified column if not exists
        await conn.execute(
            sa.text("""
                ALTER TABLE attendances 
                ADD COLUMN IF NOT EXISTS telegram_notified BOOLEAN NOT NULL DEFAULT FALSE
            """)
        )
        logger.info("Database schema updated (telegram_notified column ensured)")
        
        # Add composite indexes for performance
        await conn.execute(
            sa.text("""
                CREATE INDEX IF NOT EXISTS ix_attendance_date_status 
                ON attendances (date, status)
            """)
        )
        await conn.execute(
            sa.text("""
                CREATE INDEX IF NOT EXISTS ix_attendance_student_date 
                ON attendances (student_id, date)
            """)
        )
        await conn.execute(
            sa.text("""
                CREATE INDEX IF NOT EXISTS ix_students_group_active 
                ON students (group_id, is_active)
            """)
        )
        logger.info("Database indexes ensured")
        
        # Add week_type column to schedules if not exists
        await conn.execute(
            sa.text("""
                ALTER TABLE schedules 
                ADD COLUMN IF NOT EXISTS week_type VARCHAR(10) NOT NULL DEFAULT 'ALL'
            """)
        )
        logger.info("Database schema updated (week_type column ensured)")
        
        # Add missing columns to users table
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS plain_password VARCHAR(255)"))
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS refresh_token VARCHAR(500)"))
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS settings TEXT"))
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS device_tokens JSONB"))
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_first_login BOOLEAN NOT NULL DEFAULT FALSE"))
        await conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE"))
        logger.info("Database schema updated (users table columns ensured)")
        
        # Add missing columns to students table
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS commute VARCHAR(100)"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS passport VARCHAR(20)"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS jshshir VARCHAR(20)"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS gender VARCHAR(10)"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS contract_paid NUMERIC(12,2) NOT NULL DEFAULT 0"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS is_graduated BOOLEAN NOT NULL DEFAULT FALSE"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS is_leader BOOLEAN NOT NULL DEFAULT FALSE"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS mutoola_student_id VARCHAR(100)"))
        await conn.execute(sa.text("ALTER TABLE students ADD COLUMN IF NOT EXISTS extra_data TEXT"))
        logger.info("Database schema updated (students table columns ensured)")
        
        # Add missing columns to groups table
        await conn.execute(sa.text("ALTER TABLE groups ADD COLUMN IF NOT EXISTS contract_amount NUMERIC(12,2) NOT NULL DEFAULT 0"))
        await conn.execute(sa.text("ALTER TABLE groups ADD COLUMN IF NOT EXISTS mutoola_group_id VARCHAR(100)"))
        logger.info("Database schema updated (groups table columns ensured)")
        
        # Add missing columns to attendances table
        await conn.execute(sa.text("ALTER TABLE attendances ADD COLUMN IF NOT EXISTS lesson_number INTEGER"))
        await conn.execute(sa.text("ALTER TABLE attendances ADD COLUMN IF NOT EXISTS excuse_reason VARCHAR(500)"))
        await conn.execute(sa.text("ALTER TABLE attendances ADD COLUMN IF NOT EXISTS recorded_by INTEGER"))
        logger.info("Database schema updated (attendances table columns ensured)")
        
        # Add missing columns to schedules table (beyond week_type)
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS subject_code VARCHAR(50)"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS specific_date DATE"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS building VARCHAR(100)"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS teacher_id INTEGER"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS description TEXT"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS semester VARCHAR(20)"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS academic_year VARCHAR(20)"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS is_cancelled BOOLEAN NOT NULL DEFAULT FALSE"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(500)"))
        await conn.execute(sa.text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS color VARCHAR(20)"))
        logger.info("Database schema updated (schedules table columns ensured)")
        
        logger.info("Database schema updated (all table columns ensured)")

    # Add missing user roles to enum - MUST run outside transaction
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block in PostgreSQL
    # Use direct asyncpg connection (not through SQLAlchemy) to avoid auto-transaction
    import asyncpg
    
    # Parse the database URL to get connection params
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        pg_conn = await asyncpg.connect(db_url)
        try:
            # Check existing enum values first
            existing = await pg_conn.fetch(
                "SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'user_role'"
            )
            existing_values = {row['enumlabel'] for row in existing}
            logger.info(f"Existing user_role enum values: {existing_values}")
            
            needed_values = ['STUDENT', 'LEADER', 'TEACHER', 'ACADEMIC_AFFAIRS', 'REGISTRAR_OFFICE', 'DEAN', 'ADMIN', 'SUPERADMIN']
            for val in needed_values:
                if val not in existing_values:
                    try:
                        await pg_conn.execute(f"ALTER TYPE user_role ADD VALUE '{val}'")
                        logger.info(f"Added enum value: {val}")
                    except Exception as e:
                        logger.warning(f"Could not add enum value {val}: {e}")
                else:
                    logger.info(f"Enum value already exists: {val}")
        finally:
            await pg_conn.close()
    except Exception as e:
        logger.error(f"Failed to update user_role enum: {e}")
    
    logger.info("Database schema updated (all user roles ensured)")


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    await engine.dispose()
    # Close Redis
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


# ==================== Redis ====================

import redis.asyncio as aioredis

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create a shared async Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    return _redis_client
