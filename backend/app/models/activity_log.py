"""
UniControl - Activity Log Model
===============================
Activity log model for system audit trail.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import TASHKENT_TZ
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ActivityAction(str, Enum):
    """Activity action enum."""
    # Auth
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # CRUD
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # Import/Export
    IMPORT = "import"
    EXPORT = "export"
    
    # Sync
    SYNC = "sync"
    
    # AI
    AI_ANALYSIS = "ai_analysis"
    
    # Reports
    REPORT_GENERATE = "report_generate"
    REPORT_DOWNLOAD = "report_download"
    
    # Admin
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    ROLE_CHANGE = "role_change"
    
    # System
    SYSTEM = "system"
    ERROR = "error"


class ActivityLog(Base):
    """
    Activity log model.
    
    Tracks all user activities for audit purposes.
    """
    
    __tablename__ = "activity_logs"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # User
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed action"
    )
    
    # Action
    action: Mapped[ActivityAction] = mapped_column(
        SAEnum(ActivityAction),
        nullable=False,
        index=True,
        comment="Action type"
    )
    
    # Entity info
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Entity type (student, group, etc.)"
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Entity ID"
    )
    
    # Description
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Action description"
    )
    
    # Changes
    old_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Old data as JSON (for updates)"
    )
    new_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="New data as JSON (for creates/updates)"
    )
    
    # Request info
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Client IP address"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Client user agent"
    )
    
    # Additional context
    context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional context as JSON"
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, action={self.action.value}, user_id={self.user_id})>"
    
    @property
    def user_name(self) -> Optional[str]:
        """Get user name."""
        return self.user.name if self.user else None
