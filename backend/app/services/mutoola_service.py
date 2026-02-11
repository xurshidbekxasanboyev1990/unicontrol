"""
UniControl - KUAF Mutoola Service
=================================
Integration with KUAF Mutoola university API.

Author: UniControl Team
Version: 1.0.0
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import settings, now_tashkent
from app.models.student import Student
from app.models.group import Group
from app.models.mutoola import (
    MutoolaSync,
    MutoolaMapping,
    SyncType,
    SyncStatus,
    SyncDirection,
)
from app.core.exceptions import ExternalAPIException, BadRequestException


class MutoolaService:
    """KUAF Mutoola API integration service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.KUAF_API_URL
        self.api_key = settings.KUAF_API_KEY
        self.api_secret = settings.KUAF_API_SECRET
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Mutoola API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params,
                )
                
                if response.status_code == 401:
                    raise ExternalAPIException("Mutoola", "Authentication failed")
                
                if response.status_code == 403:
                    raise ExternalAPIException("Mutoola", "Access denied")
                
                if response.status_code == 404:
                    raise ExternalAPIException("Mutoola", "Resource not found")
                
                if response.status_code >= 500:
                    raise ExternalAPIException("Mutoola", "Server error")
                
                return response.json()
                
        except httpx.TimeoutException:
            raise ExternalAPIException("Mutoola", "Request timeout")
        except httpx.RequestError as e:
            raise ExternalAPIException("Mutoola", f"Connection error: {str(e)}")
    
    # ==================== SYNC OPERATIONS ====================
    
    async def sync_students(
        self,
        group_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> MutoolaSync:
        """
        Sync students from Mutoola API.
        
        Args:
            group_id: Optional group ID to sync
            user_id: User who triggered the sync
            
        Returns:
            Sync record with results
        """
        # Create sync record
        sync = MutoolaSync(
            sync_type=SyncType.STUDENTS,
            direction=SyncDirection.IMPORT,
            status=SyncStatus.RUNNING,
            triggered_by=user_id,
            is_automatic=user_id is None,
            started_at=now_tashkent(),
        )
        self.db.add(sync)
        await self.db.flush()
        
        try:
            # Fetch students from Mutoola
            params = {}
            if group_id:
                # Get group's mutoola_id
                group_result = await self.db.execute(
                    select(Group).where(Group.id == group_id)
                )
                group = group_result.scalar_one_or_none()
                if group and group.mutoola_group_id:
                    params["group_id"] = group.mutoola_group_id
            
            response = await self._make_request("GET", "/students", params=params)
            
            students_data = response.get("data", [])
            sync.total_records = len(students_data)
            
            # Process each student
            for student_data in students_data:
                try:
                    await self._process_student(student_data, sync)
                except Exception as e:
                    sync.failed_records += 1
            
            sync.status = SyncStatus.COMPLETED if sync.failed_records == 0 else SyncStatus.PARTIAL
            sync.api_response = json.dumps({"count": len(students_data)})
            
        except Exception as e:
            sync.status = SyncStatus.FAILED
            sync.error_message = str(e)
        
        sync.completed_at = now_tashkent()
        await self.db.commit()
        await self.db.refresh(sync)
        
        return sync
    
    async def _process_student(
        self,
        data: Dict[str, Any],
        sync: MutoolaSync
    ) -> None:
        """Process a single student from Mutoola data."""
        mutoola_id = str(data.get("id"))
        
        # Check if mapping exists
        mapping_result = await self.db.execute(
            select(MutoolaMapping).where(
                MutoolaMapping.entity_type == "student",
                MutoolaMapping.mutoola_id == mutoola_id
            )
        )
        mapping = mapping_result.scalar_one_or_none()
        
        # Compute hash for change detection
        data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        if mapping and mapping.sync_hash == data_hash:
            # No changes
            sync.skipped_records += 1
            return
        
        # Map Mutoola data to our model
        student_data = {
            "name": data.get("full_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "passport": data.get("passport_series"),
            "jshshir": data.get("pinfl"),
            "gender": "male" if data.get("gender") == 1 else "female",
            "mutoola_student_id": mutoola_id,
        }
        
        # Parse birth date
        birth_date = data.get("birth_date")
        if birth_date:
            try:
                student_data["birth_date"] = datetime.strptime(birth_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        # Resolve group
        mutoola_group_id = data.get("group_id")
        if mutoola_group_id:
            group_mapping_result = await self.db.execute(
                select(MutoolaMapping).where(
                    MutoolaMapping.entity_type == "group",
                    MutoolaMapping.mutoola_id == str(mutoola_group_id)
                )
            )
            group_mapping = group_mapping_result.scalar_one_or_none()
            if group_mapping:
                student_data["group_id"] = group_mapping.local_id
        
        if mapping:
            # Update existing student
            await self.db.execute(
                update(Student)
                .where(Student.id == mapping.local_id)
                .values(**student_data)
            )
            sync.updated_records += 1
            
            # Update mapping
            mapping.sync_hash = data_hash
            mapping.last_synced_at = now_tashkent()
            mapping.mutoola_data = json.dumps(data)
        else:
            # Create new student
            # Generate student_id
            year = now_tashkent().year
            prefix = f"ST-{year}-"
            max_result = await self.db.execute(
                select(Student.student_id)
                .where(Student.student_id.like(f"{prefix}%"))
                .order_by(Student.student_id.desc())
                .limit(1)
            )
            max_id = max_result.scalar()
            num = int(max_id.split("-")[-1]) + 1 if max_id else 1
            student_data["student_id"] = f"{prefix}{num:04d}"
            
            student = Student(**student_data)
            self.db.add(student)
            await self.db.flush()
            
            # Create mapping
            new_mapping = MutoolaMapping(
                entity_type="student",
                local_id=student.id,
                mutoola_id=mutoola_id,
                mutoola_data=json.dumps(data),
                sync_hash=data_hash,
                last_synced_at=now_tashkent(),
            )
            self.db.add(new_mapping)
            
            sync.created_records += 1
        
        sync.processed_records += 1
    
    async def sync_groups(
        self,
        user_id: Optional[int] = None
    ) -> MutoolaSync:
        """Sync groups from Mutoola API."""
        sync = MutoolaSync(
            sync_type=SyncType.GROUPS,
            direction=SyncDirection.IMPORT,
            status=SyncStatus.RUNNING,
            triggered_by=user_id,
            is_automatic=user_id is None,
            started_at=now_tashkent(),
        )
        self.db.add(sync)
        await self.db.flush()
        
        try:
            response = await self._make_request("GET", "/groups")
            groups_data = response.get("data", [])
            sync.total_records = len(groups_data)
            
            for group_data in groups_data:
                try:
                    await self._process_group(group_data, sync)
                except Exception:
                    sync.failed_records += 1
            
            sync.status = SyncStatus.COMPLETED if sync.failed_records == 0 else SyncStatus.PARTIAL
            
        except Exception as e:
            sync.status = SyncStatus.FAILED
            sync.error_message = str(e)
        
        sync.completed_at = now_tashkent()
        await self.db.commit()
        
        return sync
    
    async def _process_group(
        self,
        data: Dict[str, Any],
        sync: MutoolaSync
    ) -> None:
        """Process a single group from Mutoola data."""
        mutoola_id = str(data.get("id"))
        
        mapping_result = await self.db.execute(
            select(MutoolaMapping).where(
                MutoolaMapping.entity_type == "group",
                MutoolaMapping.mutoola_id == mutoola_id
            )
        )
        mapping = mapping_result.scalar_one_or_none()
        
        group_data = {
            "name": data.get("name"),
            "course_year": data.get("course", 1),
            "department": data.get("department"),
            "faculty": data.get("faculty"),
            "mutoola_group_id": mutoola_id,
        }
        
        if mapping:
            await self.db.execute(
                update(Group)
                .where(Group.id == mapping.local_id)
                .values(**group_data)
            )
            sync.updated_records += 1
            mapping.last_synced_at = now_tashkent()
        else:
            group = Group(**group_data)
            self.db.add(group)
            await self.db.flush()
            
            new_mapping = MutoolaMapping(
                entity_type="group",
                local_id=group.id,
                mutoola_id=mutoola_id,
                last_synced_at=now_tashkent(),
            )
            self.db.add(new_mapping)
            sync.created_records += 1
        
        sync.processed_records += 1
    
    # ==================== DATA FETCHING ====================
    
    async def get_student(self, mutoola_id: str) -> Dict[str, Any]:
        """Fetch single student from Mutoola."""
        return await self._make_request("GET", f"/students/{mutoola_id}")
    
    async def get_groups(self) -> List[Dict[str, Any]]:
        """Fetch all groups from Mutoola."""
        response = await self._make_request("GET", "/groups")
        return response.get("data", [])
    
    async def get_schedule(self, group_id: str) -> List[Dict[str, Any]]:
        """Fetch schedule for a group from Mutoola."""
        response = await self._make_request("GET", f"/groups/{group_id}/schedule")
        return response.get("data", [])
    
    # ==================== SYNC HISTORY ====================
    
    async def get_sync_history(
        self,
        sync_type: Optional[SyncType] = None,
        limit: int = 20
    ) -> List[MutoolaSync]:
        """Get sync history."""
        query = select(MutoolaSync).order_by(MutoolaSync.created_at.desc())
        
        if sync_type:
            query = query.where(MutoolaSync.sync_type == sync_type)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_last_sync(
        self,
        sync_type: SyncType
    ) -> Optional[MutoolaSync]:
        """Get last successful sync of a type."""
        result = await self.db.execute(
            select(MutoolaSync)
            .where(MutoolaSync.sync_type == sync_type)
            .where(MutoolaSync.status.in_([SyncStatus.COMPLETED, SyncStatus.PARTIAL]))
            .order_by(MutoolaSync.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Mutoola API."""
        try:
            response = await self._make_request("GET", "/ping")
            return {
                "status": "connected",
                "response": response,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }
