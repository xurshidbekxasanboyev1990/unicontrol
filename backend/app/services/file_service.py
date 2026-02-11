"""
UniControl - File Service
=========================
Business logic for file management operations.

This service handles:
- File upload and storage
- File retrieval and streaming
- Folder management
- File type detection
- Storage statistics

Author: UniControl Team
Version: 1.0.0
"""

import os
import uuid
import shutil
import mimetypes
from datetime import datetime
from typing import Optional, List, Tuple
from pathlib import Path
from loguru import logger

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import UploadFile, HTTPException

from app.models.file import File, Folder, FileType
from app.schemas.file import (
    FileCreate, FileUpdate, FileResponse,
    FolderCreate, FolderUpdate, FolderResponse,
    FileManagerResponse, StorageStats
)
from app.config import settings, now_tashkent


# File type mappings based on extension
FILE_TYPE_MAPPING = {
    # Documents
    'pdf': FileType.DOCUMENT,
    'doc': FileType.DOCUMENT,
    'docx': FileType.DOCUMENT,
    'txt': FileType.DOCUMENT,
    'rtf': FileType.DOCUMENT,
    'odt': FileType.DOCUMENT,
    
    # Spreadsheets
    'xls': FileType.SPREADSHEET,
    'xlsx': FileType.SPREADSHEET,
    'csv': FileType.SPREADSHEET,
    'ods': FileType.SPREADSHEET,
    
    # Images
    'jpg': FileType.IMAGE,
    'jpeg': FileType.IMAGE,
    'png': FileType.IMAGE,
    'gif': FileType.IMAGE,
    'webp': FileType.IMAGE,
    'bmp': FileType.IMAGE,
    'svg': FileType.IMAGE,
    
    # Videos
    'mp4': FileType.VIDEO,
    'avi': FileType.VIDEO,
    'mov': FileType.VIDEO,
    'wmv': FileType.VIDEO,
    'mkv': FileType.VIDEO,
    'webm': FileType.VIDEO,
    
    # Archives
    'zip': FileType.ARCHIVE,
    'rar': FileType.ARCHIVE,
    '7z': FileType.ARCHIVE,
    'tar': FileType.ARCHIVE,
    'gz': FileType.ARCHIVE,
}

# Maximum file sizes by type (in bytes)
MAX_FILE_SIZES = {
    FileType.DOCUMENT: 50 * 1024 * 1024,     # 50 MB
    FileType.SPREADSHEET: 30 * 1024 * 1024,  # 30 MB
    FileType.IMAGE: 20 * 1024 * 1024,        # 20 MB
    FileType.VIDEO: 500 * 1024 * 1024,       # 500 MB
    FileType.ARCHIVE: 200 * 1024 * 1024,     # 200 MB
    FileType.OTHER: 50 * 1024 * 1024,        # 50 MB
}


class FileService:
    """
    Service class for file management operations.
    
    Provides methods for:
    - File upload/download
    - File metadata management
    - Folder operations
    - Storage statistics
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize file service.
        
        Args:
            db: AsyncSession database connection
        """
        self.db = db
        self.upload_dir = Path(getattr(settings, 'UPLOAD_DIR', 'uploads'))
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_type(self, filename: str) -> FileType:
        """
        Determine file type based on extension.
        
        Args:
            filename: Original filename
            
        Returns:
            FileType enum value
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        return FILE_TYPE_MAPPING.get(ext, FileType.OTHER)
    
    def _get_mime_type(self, filename: str) -> str:
        """
        Get MIME type for filename.
        
        Args:
            filename: Original filename
            
        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def _generate_stored_name(self, original_name: str) -> str:
        """
        Generate unique stored filename using UUID.
        
        Args:
            original_name: Original filename
            
        Returns:
            UUID-based stored filename with original extension
        """
        ext = original_name.rsplit('.', 1)[-1] if '.' in original_name else ''
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{ext}" if ext else unique_id
    
    def _get_user_folder(self, user_id: int) -> Path:
        """
        Get user's upload folder path.
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user's folder
        """
        user_folder = self.upload_dir / str(user_id)
        user_folder.mkdir(parents=True, exist_ok=True)
        return user_folder
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: int,
        folder_id: Optional[int] = None,
        group_id: Optional[int] = None,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> File:
        """
        Upload and save a file.
        
        Args:
            file: Uploaded file object
            user_id: Owner user ID
            folder_id: Optional parent folder ID
            group_id: Optional associated group ID
            description: Optional file description
            is_public: Public accessibility flag
            
        Returns:
            Created File object
            
        Raises:
            HTTPException: If file size exceeds limit or upload fails
        """
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Fayl nomi bo'sh bo'lmasligi kerak")
        
        # Determine file type
        file_type = self._get_file_type(file.filename)
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES[FileType.OTHER])
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=400, 
                detail=f"Fayl hajmi {max_mb:.0f} MB dan oshmasligi kerak"
            )
        
        # Generate stored name and path
        stored_name = self._generate_stored_name(file.filename)
        user_folder = self._get_user_folder(user_id)
        file_path = user_folder / stored_name
        
        # Save file to disk
        try:
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Faylni saqlashda xatolik: {str(e)}")
        
        # Get extension
        extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else None
        
        # Create database record
        db_file = File(
            name=file.filename,
            stored_name=stored_name,
            path=str(file_path),
            size=file_size,
            file_type=file_type,
            mime_type=self._get_mime_type(file.filename),
            extension=extension,
            folder_id=folder_id,
            user_id=user_id,
            group_id=group_id,
            description=description,
            is_public=is_public
        )
        
        self.db.add(db_file)
        await self.db.commit()
        await self.db.refresh(db_file)
        
        return db_file
    
    async def get_file(self, file_id: int, user_id: Optional[int] = None) -> Optional[File]:
        """
        Get file by ID.
        
        Args:
            file_id: File ID
            user_id: Optional user ID for permission check
            
        Returns:
            File object or None
        """
        query = select(File).where(File.id == file_id)
        
        # If user_id provided, check ownership or public
        if user_id:
            query = query.where(
                or_(File.user_id == user_id, File.is_public == True)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_files(
        self,
        user_id: int,
        folder_id: Optional[int] = None,
        file_type: Optional[FileType] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[File], int]:
        """
        List files with filters.
        
        Args:
            user_id: User ID
            folder_id: Filter by folder ID
            file_type: Filter by file type
            search: Search in filename
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (files list, total count)
        """
        # Base query - user's files or public files
        query = select(File).where(
            or_(File.user_id == user_id, File.is_public == True)
        )
        
        # Apply filters
        if folder_id is not None:
            query = query.where(File.folder_id == folder_id)
        elif folder_id is None:
            # Root folder - files without folder
            query = query.where(File.folder_id.is_(None))
        
        if file_type:
            query = query.where(File.file_type == file_type)
        
        if search:
            query = query.where(File.name.ilike(f"%{search}%"))
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(File.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        files = result.scalars().all()
        
        return list(files), total
    
    async def update_file(
        self,
        file_id: int,
        user_id: int,
        data: FileUpdate
    ) -> Optional[File]:
        """
        Update file metadata.
        
        Args:
            file_id: File ID
            user_id: User ID (must be owner)
            data: Update data
            
        Returns:
            Updated File or None
        """
        file = await self.get_file(file_id, user_id)
        if not file or file.user_id != user_id:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(file, field, value)
        
        file.updated_at = now_tashkent()
        await self.db.commit()
        await self.db.refresh(file)
        
        return file
    
    async def delete_file(self, file_id: int, user_id: int) -> bool:
        """
        Delete a file.
        
        Args:
            file_id: File ID
            user_id: User ID (must be owner)
            
        Returns:
            True if deleted, False otherwise
        """
        file = await self.get_file(file_id, user_id)
        if not file or file.user_id != user_id:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(file.path):
                os.remove(file.path)
        except Exception as e:
            logger.warning(f"Failed to delete physical file {file.path}: {e}")
        
        # Delete database record
        await self.db.delete(file)
        await self.db.commit()
        
        return True
    
    async def increment_download_count(self, file_id: int) -> None:
        """Increment file download counter."""
        file = await self.db.get(File, file_id)
        if file:
            file.download_count += 1
            await self.db.commit()
    
    # ==================== FOLDER OPERATIONS ====================
    
    async def create_folder(
        self,
        data: FolderCreate,
        user_id: int
    ) -> Folder:
        """
        Create a new folder.
        
        Args:
            data: Folder creation data
            user_id: Owner user ID
            
        Returns:
            Created Folder object
        """
        # Determine path
        if data.parent_id:
            parent = await self.db.get(Folder, data.parent_id)
            if parent:
                path = f"{parent.path}/{data.name}"
            else:
                path = f"/{data.name}"
        else:
            path = f"/{data.name}"
        
        folder = Folder(
            name=data.name,
            path=path,
            parent_id=data.parent_id,
            user_id=user_id,
            group_id=data.group_id,
            description=data.description,
            color=data.color,
            icon=data.icon
        )
        
        self.db.add(folder)
        await self.db.commit()
        await self.db.refresh(folder)
        
        return folder
    
    async def get_folder(self, folder_id: int, user_id: Optional[int] = None) -> Optional[Folder]:
        """
        Get folder by ID.
        
        Args:
            folder_id: Folder ID
            user_id: Optional user ID for permission check
            
        Returns:
            Folder object or None
        """
        query = select(Folder).where(Folder.id == folder_id)
        
        if user_id:
            query = query.where(Folder.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_folders(
        self,
        user_id: int,
        parent_id: Optional[int] = None
    ) -> List[Folder]:
        """
        List folders for user.
        
        Args:
            user_id: User ID
            parent_id: Parent folder ID (None for root)
            
        Returns:
            List of folders
        """
        query = select(Folder).where(Folder.user_id == user_id)
        
        if parent_id is not None:
            query = query.where(Folder.parent_id == parent_id)
        else:
            query = query.where(Folder.parent_id.is_(None))
        
        query = query.order_by(Folder.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_folder(
        self,
        folder_id: int,
        user_id: int,
        data: FolderUpdate
    ) -> Optional[Folder]:
        """
        Update folder.
        
        Args:
            folder_id: Folder ID
            user_id: User ID (must be owner)
            data: Update data
            
        Returns:
            Updated Folder or None
        """
        folder = await self.get_folder(folder_id, user_id)
        if not folder or folder.user_id != user_id:
            return None
        
        if folder.is_system:
            raise HTTPException(status_code=400, detail="Tizim papkasini o'zgartirib bo'lmaydi")
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)
        
        # Update path if name changed
        if 'name' in update_data:
            if folder.parent_id:
                parent = await self.db.get(Folder, folder.parent_id)
                folder.path = f"{parent.path}/{folder.name}" if parent else f"/{folder.name}"
            else:
                folder.path = f"/{folder.name}"
        
        folder.updated_at = now_tashkent()
        await self.db.commit()
        await self.db.refresh(folder)
        
        return folder
    
    async def delete_folder(self, folder_id: int, user_id: int) -> bool:
        """
        Delete folder and all its contents.
        
        Args:
            folder_id: Folder ID
            user_id: User ID (must be owner)
            
        Returns:
            True if deleted, False otherwise
        """
        folder = await self.get_folder(folder_id, user_id)
        if not folder or folder.user_id != user_id:
            return False
        
        if folder.is_system:
            raise HTTPException(status_code=400, detail="Tizim papkasini o'chirib bo'lmaydi")
        
        await self.db.delete(folder)
        await self.db.commit()
        
        return True
    
    # ==================== COMBINED OPERATIONS ====================
    
    async def get_file_manager_data(
        self,
        user_id: int,
        folder_id: Optional[int] = None
    ) -> FileManagerResponse:
        """
        Get data for file manager view.
        
        Args:
            user_id: User ID
            folder_id: Current folder ID (None for root)
            
        Returns:
            FileManagerResponse with folders and files
        """
        # Get folders
        folders = await self.list_folders(user_id, folder_id)
        
        # Get files
        files, total_files = await self.list_files(user_id, folder_id)
        
        # Build breadcrumbs
        breadcrumbs = [{"name": "Asosiy", "path": "/", "id": None}]
        if folder_id:
            folder = await self.get_folder(folder_id, user_id)
            if folder:
                # Build path from folder
                path_parts = folder.path.strip('/').split('/')
                current_path = ""
                for part in path_parts:
                    current_path += f"/{part}"
                    breadcrumbs.append({
                        "name": part,
                        "path": current_path,
                        "id": folder.id if current_path == folder.path else None
                    })
        
        current_path = folder.path if folder_id and folder else "/"
        
        return FileManagerResponse(
            current_path=current_path,
            breadcrumbs=breadcrumbs,
            folders=[FolderResponse.model_validate(f) for f in folders],
            files=[FileResponse.model_validate(f) for f in files],
            total_folders=len(folders),
            total_files=total_files
        )
    
    async def get_storage_stats(self, user_id: int) -> StorageStats:
        """
        Get storage statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            StorageStats object
        """
        # Count files
        files_query = select(func.count()).select_from(File).where(File.user_id == user_id)
        files_result = await self.db.execute(files_query)
        total_files = files_result.scalar() or 0
        
        # Count folders
        folders_query = select(func.count()).select_from(Folder).where(Folder.user_id == user_id)
        folders_result = await self.db.execute(folders_query)
        total_folders = folders_result.scalar() or 0
        
        # Total size
        size_query = select(func.sum(File.size)).where(File.user_id == user_id)
        size_result = await self.db.execute(size_query)
        total_size = size_result.scalar() or 0
        
        # Files by type
        type_query = select(
            File.file_type, func.count()
        ).where(File.user_id == user_id).group_by(File.file_type)
        type_result = await self.db.execute(type_query)
        files_by_type = {str(row[0].value): row[1] for row in type_result.all()}
        
        # Recent uploads
        recent_query = select(File).where(
            File.user_id == user_id
        ).order_by(File.created_at.desc()).limit(5)
        recent_result = await self.db.execute(recent_query)
        recent_files = list(recent_result.scalars().all())
        
        # Format size
        if total_size < 1024:
            size_formatted = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_formatted = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_formatted = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_formatted = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        
        return StorageStats(
            total_files=total_files,
            total_folders=total_folders,
            total_size=total_size,
            total_size_formatted=size_formatted,
            files_by_type=files_by_type,
            recent_uploads=[FileResponse.model_validate(f) for f in recent_files]
        )
