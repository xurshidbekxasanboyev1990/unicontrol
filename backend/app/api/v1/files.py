"""
UniControl - File Routes
========================
File management API endpoints.

This module provides:
- File upload/download endpoints
- File metadata management
- Folder CRUD operations
- File manager view data
- Storage statistics

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File as FastAPIFile, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.database import get_db
from app.services.file_service import FileService
from app.schemas.file import (
    FileCreate, FileUpdate, FileResponse as FileResponseSchema,
    FileListResponse, FileUploadResponse,
    FolderCreate, FolderUpdate, FolderResponse, FolderListResponse,
    FileManagerResponse, StorageStats
)
from app.models.file import FileType
from app.core.dependencies import get_current_active_user, require_leader
from app.models.user import User

router = APIRouter()


# ==================== FILE ENDPOINTS ====================

@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(..., description="Yuklanadigan fayl"),
    folder_id: Optional[int] = Query(None, description="Papka ID"),
    group_id: Optional[int] = Query(None, description="Guruh ID"),
    description: Optional[str] = Query(None, max_length=1000, description="Fayl tavsifi"),
    is_public: bool = Query(False, description="Ommaviy kirish"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new file.
    
    - **file**: File to upload (required)
    - **folder_id**: Parent folder ID (optional)
    - **group_id**: Associated group ID (optional)
    - **description**: File description (optional)
    - **is_public**: Public accessibility flag
    
    Returns the uploaded file information.
    
    File size limits:
    - Documents: 50 MB
    - Spreadsheets: 30 MB
    - Images: 20 MB
    - Videos: 500 MB
    - Archives: 200 MB
    """
    service = FileService(db)
    
    uploaded_file = await service.upload_file(
        file=file,
        user_id=current_user.id,
        folder_id=folder_id,
        group_id=group_id,
        description=description,
        is_public=is_public
    )
    
    # Generate URL for file access
    file_url = f"/api/v1/files/{uploaded_file.id}/download"
    
    return FileUploadResponse(
        id=uploaded_file.id,
        name=uploaded_file.name,
        size=uploaded_file.size,
        file_type=uploaded_file.file_type,
        url=file_url,
        message="Fayl muvaffaqiyatli yuklandi"
    )


@router.get("", response_model=FileListResponse)
async def list_files(
    folder_id: Optional[int] = Query(None, description="Papka ID (root uchun None)"),
    file_type: Optional[FileType] = Query(None, description="Fayl turi filtri"),
    search: Optional[str] = Query(None, max_length=100, description="Qidiruv so'zi"),
    page: int = Query(1, ge=1, description="Sahifa raqami"),
    page_size: int = Query(50, ge=1, le=200, description="Sahifadagi elementlar"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List files with optional filters.
    
    - **folder_id**: Filter by folder (None for root)
    - **file_type**: Filter by file type
    - **search**: Search in filename
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (max 200)
    
    Returns paginated list of files.
    """
    service = FileService(db)
    
    files, total = await service.list_files(
        user_id=current_user.id,
        folder_id=folder_id,
        file_type=file_type,
        search=search,
        page=page,
        page_size=page_size
    )
    
    return FileListResponse(
        items=[FileResponseSchema.model_validate(f) for f in files],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/manager", response_model=FileManagerResponse)
async def get_file_manager(
    folder_id: Optional[int] = Query(None, description="Joriy papka ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get file manager view data.
    
    Returns folders and files for the current path,
    along with breadcrumb navigation.
    
    - **folder_id**: Current folder ID (None for root)
    """
    service = FileService(db)
    return await service.get_file_manager_data(
        user_id=current_user.id,
        folder_id=folder_id
    )


@router.get("/stats", response_model=StorageStats)
async def get_storage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get storage statistics for current user.
    
    Returns:
    - Total files and folders count
    - Total storage used
    - Files by type breakdown
    - Recent uploads
    """
    service = FileService(db)
    return await service.get_storage_stats(current_user.id)


@router.get("/{file_id}", response_model=FileResponseSchema)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get file metadata by ID.
    
    Returns file information without the actual file content.
    Use `/files/{file_id}/download` to download the file.
    """
    service = FileService(db)
    file = await service.get_file(file_id, current_user.id)
    
    if not file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi")
    
    return FileResponseSchema.model_validate(file)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a file.
    
    Returns the file as a download response with appropriate
    content-type and filename headers.
    
    Increments the download counter.
    """
    service = FileService(db)
    file = await service.get_file(file_id, current_user.id)
    
    if not file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi")
    
    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="Fayl diskda topilmadi")
    
    # Increment download count
    await service.increment_download_count(file_id)
    
    return FileResponse(
        path=file.path,
        filename=file.name,
        media_type=file.mime_type or "application/octet-stream"
    )


@router.put("/{file_id}", response_model=FileResponseSchema)
async def update_file(
    file_id: int,
    data: FileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update file metadata.
    
    Can update:
    - **name**: Filename (display name, not stored name)
    - **description**: File description
    - **folder_id**: Move to different folder
    - **is_public**: Change accessibility
    """
    service = FileService(db)
    file = await service.update_file(file_id, current_user.id, data)
    
    if not file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi yoki ruxsat yo'q")
    
    return FileResponseSchema.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a file.
    
    Removes both the database record and the physical file.
    Only the file owner can delete their files.
    """
    service = FileService(db)
    deleted = await service.delete_file(file_id, current_user.id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Fayl topilmadi yoki ruxsat yo'q")
    
    return None


# ==================== FOLDER ENDPOINTS ====================

@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    data: FolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new folder.
    
    - **name**: Folder name (required)
    - **parent_id**: Parent folder ID (None for root)
    - **group_id**: Associated group ID (optional)
    - **description**: Folder description (optional)
    - **color**: Folder color for UI (optional)
    - **icon**: Custom icon name (optional)
    """
    service = FileService(db)
    folder = await service.create_folder(data, current_user.id)
    return FolderResponse.model_validate(folder)


@router.get("/folders", response_model=FolderListResponse)
async def list_folders(
    parent_id: Optional[int] = Query(None, description="Ota papka ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List folders.
    
    - **parent_id**: Parent folder ID (None for root level)
    
    Returns list of folders at the specified level.
    """
    service = FileService(db)
    folders = await service.list_folders(current_user.id, parent_id)
    
    return FolderListResponse(
        items=[FolderResponse.model_validate(f) for f in folders],
        total=len(folders)
    )


@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get folder by ID.
    """
    service = FileService(db)
    folder = await service.get_folder(folder_id, current_user.id)
    
    if not folder:
        raise HTTPException(status_code=404, detail="Papka topilmadi")
    
    return FolderResponse.model_validate(folder)


@router.put("/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: int,
    data: FolderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update folder.
    
    Can update:
    - **name**: Folder name
    - **description**: Folder description
    - **parent_id**: Move to different parent
    - **color**: Folder color
    - **icon**: Custom icon
    
    Note: System folders cannot be modified.
    """
    service = FileService(db)
    folder = await service.update_folder(folder_id, current_user.id, data)
    
    if not folder:
        raise HTTPException(status_code=404, detail="Papka topilmadi yoki ruxsat yo'q")
    
    return FolderResponse.model_validate(folder)


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a folder and all its contents.
    
    Warning: This will delete all files and subfolders inside!
    System folders cannot be deleted.
    """
    service = FileService(db)
    deleted = await service.delete_folder(folder_id, current_user.id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Papka topilmadi yoki ruxsat yo'q")
    
    return None
