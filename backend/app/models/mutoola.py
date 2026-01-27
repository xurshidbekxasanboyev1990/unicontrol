"""
UniControl - Mutoola Sync Model
===============================
Model for tracking KUAF Mutoola API synchronization.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SyncType(str, Enum):
    """Sync type enum."""
    STUDENTS = "students"
    GROUPS = "groups"
    SCHEDULE = "schedule"
    PAYMENTS = "payments"
    FULL = "full"


class SyncStatus(str, Enum):
    """Sync status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncDirection(str, Enum):
    """Sync direction enum."""
    IMPORT = "import"  # From Mutoola to UniControl
    EXPORT = "export"  # From UniControl to Mutoola
    BIDIRECTIONAL = "bidirectional"


class MutoolaSync(Base):
    """
    Mutoola sync model.
    
    Tracks synchronization history with KUAF Mutoola API.
    """
    
    __tablename__ = "mutoola_syncs"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Sync info
    sync_type: Mapped[SyncType] = mapped_column(
        SAEnum(SyncType),
        nullable=False,
        index=True,
        comment="Type of sync"
    )
    direction: Mapped[SyncDirection] = mapped_column(
        SAEnum(SyncDirection),
        nullable=False,
        default=SyncDirection.IMPORT,
        comment="Sync direction"
    )
    
    # Status
    status: Mapped[SyncStatus] = mapped_column(
        SAEnum(SyncStatus),
        nullable=False,
        default=SyncStatus.PENDING,
        index=True,
        comment="Sync status"
    )
    
    # Stats
    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total records to sync"
    )
    processed_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Records processed"
    )
    created_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="New records created"
    )
    updated_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Records updated"
    )
    skipped_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Records skipped"
    )
    failed_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Records failed"
    )
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Start time"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Completion time"
    )
    
    # API response
    api_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="API response as JSON"
    )
    
    # Errors
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message"
    )
    error_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed error info as JSON"
    )
    
    # Triggered by
    triggered_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who triggered sync"
    )
    is_automatic: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Automatic sync vs manual"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    triggered_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[triggered_by],
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        return f"<MutoolaSync(id={self.id}, type={self.sync_type.value}, status={self.status.value})>"
    
    @property
    def progress_percentage(self) -> float:
        """Get sync progress percentage."""
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get sync duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Get success rate."""
        if self.processed_records == 0:
            return 0
        return ((self.processed_records - self.failed_records) / self.processed_records) * 100


class MutoolaMapping(Base):
    """
    Mutoola ID mapping model.
    
    Maps local IDs to Mutoola IDs for syncing.
    """
    
    __tablename__ = "mutoola_mappings"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Entity type
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Entity type (student, group, etc.)"
    )
    
    # IDs
    local_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Local database ID"
    )
    mutoola_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Mutoola API ID"
    )
    
    # Additional Mutoola data
    mutoola_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional Mutoola data as JSON"
    )
    
    # Sync info
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last sync time"
    )
    sync_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="Hash of last synced data for change detection"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Mapping active status"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Unique constraint
    __table_args__ = (
        # One mapping per entity type and local ID
        {"sqlite_autoincrement": True},
    )
    
    def __repr__(self) -> str:
        return f"<MutoolaMapping(entity={self.entity_type}, local={self.local_id}, mutoola={self.mutoola_id})>"
