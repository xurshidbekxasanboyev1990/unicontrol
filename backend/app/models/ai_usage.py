"""
UniControl - AI Usage Model
============================
Track AI token usage per user per month with cost limits.

Student limit: 1000 UZS/month
Staff (leader/admin/super) limit: 1500 UZS/month

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base


class AIUsage(Base):
    """
    AI Usage tracking per user per month.
    
    Stores cumulative token usage and estimated cost in UZS.
    Each row = one user for one month (YYYY-MM).
    """
    
    __tablename__ = "ai_usage"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # User reference
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Month period (e.g., "2026-02")
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    
    # Token usage
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Request count
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Estimated cost in UZS
    cost_uzs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Limit in UZS (set based on role at creation)
    limit_uzs: Mapped[float] = mapped_column(Float, default=1000.0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        onupdate=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_ai_usage_user_month", "user_id", "month", unique=True),
    )
    
    # Relationship
    user = relationship("User", backref="ai_usage_records")
