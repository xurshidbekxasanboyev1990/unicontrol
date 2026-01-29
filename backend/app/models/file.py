"""
UniControl - File Model
=======================
Database model for file storage and management.

This model handles:
- File uploads (documents, images, videos, archives)
- Folder organization
- File metadata (size, type, mime type)
- User ownership and permissions

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Text, Boolean, BigInteger, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, backref

from app.database import Base


class FileType(str, Enum):
    """
    File type enumeration.
    Used to categorize files for filtering and display.
    """
    DOCUMENT = "document"      # PDF, DOC, DOCX, TXT
    SPREADSHEET = "spreadsheet"  # XLS, XLSX, CSV
    IMAGE = "image"            # JPG, PNG, GIF, WEBP
    VIDEO = "video"            # MP4, AVI, MOV
    ARCHIVE = "archive"        # ZIP, RAR, 7Z
    OTHER = "other"            # Any other file type


class File(Base):
    """
    File database model.
    
    Stores uploaded files with metadata including:
    - Original filename and stored path
    - File size and type
    - Upload date and user
    - Optional folder organization
    
    Attributes:
        id: Primary key
        name: Original filename
        stored_name: UUID-based stored filename (for security)
        path: Full storage path
        size: File size in bytes
        file_type: Categorized file type (document, image, etc.)
        mime_type: MIME type string (application/pdf, image/jpeg, etc.)
        folder_id: Optional parent folder reference
        user_id: Owner user ID
        group_id: Optional group association
        description: Optional file description
        is_public: Whether file is publicly accessible
        download_count: Number of times file was downloaded
        created_at: Upload timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # File information
    name = Column(String(255), nullable=False, comment="Original filename")
    stored_name = Column(String(255), nullable=False, unique=True, comment="UUID-based stored name")
    path = Column(String(500), nullable=False, comment="Full storage path")
    size = Column(BigInteger, nullable=False, default=0, comment="File size in bytes")
    
    # File type classification
    file_type = Column(
        SQLEnum(FileType), 
        nullable=False, 
        default=FileType.OTHER,
        comment="File category type"
    )
    mime_type = Column(String(100), nullable=True, comment="MIME type")
    extension = Column(String(20), nullable=True, comment="File extension without dot")
    
    # Organization
    folder_id = Column(
        Integer, 
        ForeignKey("folders.id", ondelete="SET NULL"), 
        nullable=True,
        comment="Parent folder ID"
    )
    
    # Ownership
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Owner user ID"
    )
    group_id = Column(
        Integer, 
        ForeignKey("groups.id", ondelete="SET NULL"), 
        nullable=True,
        comment="Associated group ID"
    )
    
    # Metadata
    description = Column(Text, nullable=True, comment="File description")
    is_public = Column(Boolean, default=False, comment="Public accessibility flag")
    download_count = Column(Integer, default=0, comment="Download counter")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, comment="Upload timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    folder = relationship("Folder", back_populates="files")
    user = relationship("User", backref="files")
    group = relationship("Group", backref="files")
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', type={self.file_type})>"
    
    @property
    def size_formatted(self) -> str:
        """Return human-readable file size."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"


class Folder(Base):
    """
    Folder database model.
    
    Provides hierarchical folder structure for organizing files.
    Supports nested folders with parent-child relationships.
    
    Attributes:
        id: Primary key
        name: Folder name
        path: Full path from root (e.g., /documents/reports)
        parent_id: Parent folder ID for nesting
        user_id: Owner user ID
        group_id: Optional group association
        is_system: Whether this is a system folder (cannot be deleted)
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Folder information
    name = Column(String(255), nullable=False, comment="Folder name")
    path = Column(String(500), nullable=False, default="/", comment="Full folder path")
    
    # Hierarchy
    parent_id = Column(
        Integer, 
        ForeignKey("folders.id", ondelete="CASCADE"), 
        nullable=True,
        comment="Parent folder ID"
    )
    
    # Ownership
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Owner user ID"
    )
    group_id = Column(
        Integer, 
        ForeignKey("groups.id", ondelete="SET NULL"), 
        nullable=True,
        comment="Associated group ID"
    )
    
    # Metadata
    description = Column(Text, nullable=True, comment="Folder description")
    is_system = Column(Boolean, default=False, comment="System folder flag")
    color = Column(String(20), nullable=True, comment="Folder color for UI")
    icon = Column(String(50), nullable=True, comment="Custom icon name")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="folder", cascade="all, delete-orphan")
    parent = relationship("Folder", remote_side=[id], backref="children")
    user = relationship("User", backref="folders")
    group = relationship("Group", backref="folders")
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', path='{self.path}')>"
    
    @property
    def item_count(self) -> int:
        """Return total count of files in this folder."""
        return len(self.files) if self.files else 0
