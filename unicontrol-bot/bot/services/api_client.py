import aiohttp
import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from bot.config import settings

logger = logging.getLogger(__name__)


class UniControlAPI:
    """
    API client for UniControl backend.
    Handles all communication with the main system.
    """
    
    def __init__(self):
        self.base_url = settings.api_base_url.rstrip("/")
        self.api_key = settings.api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "X-Bot-Token": settings.bot_token
                }
            )
        return self._session
    
    async def close(self):
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, params=params, json=json) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            return None
    
    # ==================== Groups API ====================
    
    async def search_groups(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for academic groups by code or name.
        
        Args:
            query: Search query (e.g., "KI_25" or "Kompyuter")
            
        Returns:
            List of matching groups
        """
        result = await self._request(
            "GET", 
            "/api/v1/groups/search",
            params={"q": query}
        )
        return result.get("items", []) if result else []
    
    async def get_group_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get group by exact code.
        
        Args:
            code: Group code (e.g., "KI_25-09")
            
        Returns:
            Group data or None
        """
        result = await self._request(
            "GET",
            f"/api/v1/groups/code/{code}"
        )
        return result
    
    async def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get group by ID"""
        return await self._request("GET", f"/api/v1/groups/{group_id}")
    
    async def list_groups(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List all groups"""
        result = await self._request(
            "GET",
            "/api/v1/groups/",
            params={"skip": skip, "limit": limit}
        )
        return result.get("items", []) if result else []
    
    # ==================== Attendance API ====================
    
    async def get_group_attendance(
        self,
        group_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get attendance records for a group.
        
        Args:
            group_id: Academic group ID
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            List of attendance records
        """
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        result = await self._request(
            "GET",
            f"/api/v1/attendance/group/{group_id}",
            params=params
        )
        return result.get("items", []) if result else []
    
    async def get_today_attendance(self, group_id: int) -> List[Dict[str, Any]]:
        """Get today's attendance for a group"""
        today = date.today()
        return await self.get_group_attendance(group_id, today, today)
    
    async def get_student_attendance(
        self,
        student_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records for a student"""
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        result = await self._request(
            "GET",
            f"/api/v1/attendance/student/{student_id}",
            params=params
        )
        return result.get("items", []) if result else []
    
    async def get_recent_attendance_updates(
        self,
        group_id: int,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get attendance records updated since a specific time.
        Used for real-time notifications.
        
        Args:
            group_id: Academic group ID
            since: Get records updated after this time
            
        Returns:
            List of updated attendance records
        """
        result = await self._request(
            "GET",
            f"/api/v1/attendance/group/{group_id}/updates",
            params={"since": since.isoformat()}
        )
        return result.get("items", []) if result else []
    
    # ==================== Students API ====================
    
    async def get_students_by_group(self, group_id: int) -> List[Dict[str, Any]]:
        """Get all students in a group"""
        result = await self._request(
            "GET",
            f"/api/v1/students/group/{group_id}"
        )
        return result.get("items", []) if result else []
    
    async def search_student(self, query: str) -> List[Dict[str, Any]]:
        """Search for students by name"""
        result = await self._request(
            "GET",
            "/api/v1/students/search",
            params={"q": query}
        )
        return result.get("items", []) if result else []
    
    async def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Get student by ID"""
        return await self._request("GET", f"/api/v1/students/{student_id}")
    
    # ==================== Schedule API ====================
    
    async def get_group_schedule(
        self,
        group_id: int,
        target_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get schedule for a group"""
        params = {}
        if target_date:
            params["date"] = target_date.isoformat()
        
        result = await self._request(
            "GET",
            f"/api/v1/schedule/group/{group_id}",
            params=params
        )
        return result.get("items", []) if result else []
    
    # ==================== Bot Specific API ====================
    
    async def register_telegram_chat(
        self,
        chat_id: int,
        group_code: str,
        chat_type: str,
        chat_title: Optional[str] = None
    ) -> bool:
        """
        Register Telegram chat for attendance notifications.
        
        Args:
            chat_id: Telegram chat ID
            group_code: Academic group code
            chat_type: Chat type (private, group, supergroup)
            chat_title: Chat title
            
        Returns:
            True if successful
        """
        result = await self._request(
            "POST",
            "/api/v1/telegram/register",
            json={
                "chat_id": chat_id,
                "group_code": group_code,
                "chat_type": chat_type,
                "chat_title": chat_title
            }
        )
        return result is not None
    
    async def unregister_telegram_chat(self, chat_id: int) -> bool:
        """Unregister Telegram chat"""
        result = await self._request(
            "DELETE",
            f"/api/v1/telegram/unregister/{chat_id}"
        )
        return result is not None
    
    async def verify_student(
        self,
        telegram_id: int,
        student_id: int,
        verification_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify student identity for personal attendance access.
        
        Args:
            telegram_id: Telegram user ID
            student_id: UniControl student ID
            verification_code: Verification code from system
            
        Returns:
            Student data if verified
        """
        result = await self._request(
            "POST",
            "/api/v1/telegram/verify",
            json={
                "telegram_id": telegram_id,
                "student_id": student_id,
                "verification_code": verification_code
            }
        )
        return result


# Singleton instance
api_client = UniControlAPI()
