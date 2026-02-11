"""
UniControl - File Schemas
=========================
Pydantic schemas for file operations.

These schemas handle:
- File upload/creation validation
- File response serialization
- Folder management
- File listing and filtering

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.file import FileType


# ==================== FILE SCHEMAS ====================

class FileBase(BaseModel):
    """
    Base file schema with common fields.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Original filename")
    description: Optional[str] = Field(None, max_length=1000, description="File description")
    folder_id: Optional[int] = Field(None, description="Parent folder ID")
    group_id: Optional[int] = Field(None, description="Associated group ID")
    is_public: bool = Field(False, description="Public accessibility flag")


class FileCreate(BaseModel):
    """
    Schema for file creation (metadata only, actual file uploaded separately).
    """
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    folder_id: Optional[int] = None
    group_id: Optional[int] = None
    is_public: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class FileUpdate(BaseModel):
    """
    Schema for file metadata update.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    folder_id: Optional[int] = None
    is_public: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class FileResponse(BaseModel):
    """
    Schema for file response.
    Includes all file metadata for frontend display.
    """
    id: int
    name: str
    stored_name: str
    path: str
    size: int
    size_formatted: str
    file_type: FileType
    mime_type: Optional[str]
    extension: Optional[str]
    folder_id: Optional[int]
    user_id: int
    group_id: Optional[int]
    description: Optional[str]
    is_public: bool
    download_count: int
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    """
    Paginated file list response.
    """
    items: List[FileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """
    Response after successful file upload.
    """
    id: int
    name: str
    size: int
    file_type: FileType
    url: str
    message: str = "Fayl muvaffaqiyatli yuklandi"
    
    model_config = ConfigDict(from_attributes=True)


# ==================== FOLDER SCHEMAS ====================

class FolderBase(BaseModel):
    """
    Base folder schema.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Folder name")
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)


class FolderCreate(FolderBase):
    """
    Schema for folder creation.
    """
    parent_id: Optional[int] = Field(None, description="Parent folder ID")
    group_id: Optional[int] = Field(None, description="Associated group ID")
    
    model_config = ConfigDict(from_attributes=True)


class FolderUpdate(BaseModel):
    """
    Schema for folder update.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FolderResponse(BaseModel):
    """
    Schema for folder response.
    """
    id: int
    name: str
    path: str
    parent_id: Optional[int]
    user_id: int
    group_id: Optional[int]
    description: Optional[str]
    is_system: bool
    color: Optional[str]
    icon: Optional[str]
    item_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FolderListResponse(BaseModel):
    """
    Paginated folder list response.
    """
    items: List[FolderResponse]
    total: int
    
    model_config = ConfigDict(from_attributes=True)


class FolderWithContents(FolderResponse):
    """
    Folder with its contents (subfolders and files).
    """
    subfolders: List[FolderResponse] = []
    files: List[FileResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ==================== COMBINED SCHEMAS ====================

class FileManagerResponse(BaseModel):
    """
    Response for file manager view.
    Contains folders and files for current path.
    """
    current_path: str
    breadcrumbs: List[dict]
    folders: List[FolderResponse]
    files: List[FileResponse]
    total_folders: int
    total_files: int
    
    model_config = ConfigDict(from_attributes=True)


class StorageStats(BaseModel):
    """
    Storage statistics for user/group.
    """
    total_files: int
    total_folders: int
    total_size: int
    total_size_formatted: str
    files_by_type: dict
    recent_uploads: List[FileResponse]
    
    model_config = ConfigDict(from_attributes=True)
