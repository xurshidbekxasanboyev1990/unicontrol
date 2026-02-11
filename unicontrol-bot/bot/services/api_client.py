import aiohttp
import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from bot.config import settings

logger = logging.getLogger(__name__)


class UniControlAPI:
    """
    API client for UniControl backend.
    Handles all communication via /api/v1/telegram/* endpoints
    which use X-Bot-Token authentication.
    """
    
    def __init__(self):
        # base_url should be like http://backend:8000 (no /api/v1)
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
                },
                timeout=aiohttp.ClientTimeout(total=30)
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
            logger.debug(f"API request: {method} {url}")
            async with session.request(method, url, params=params, json=json) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.debug(f"API 404: {url}")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status} {url}: {error_text}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Request error ({url}): {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error ({url}): {e}")
            return None
    
    # ==================== Groups API (via /telegram) ====================
    
    async def search_groups(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for academic groups by code or name.
        Uses bot-specific endpoint with X-Bot-Token auth.
        """
        result = await self._request(
            "GET", 
            "/api/v1/telegram/groups/search",
            params={"q": query}
        )
        return result.get("items", []) if result else []
    
    async def get_group_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get group by exact code."""
        result = await self._request(
            "GET",
            f"/api/v1/telegram/groups/code/{code}"
        )
        return result
    
    async def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get group by ID"""
        return await self._request("GET", f"/api/v1/telegram/groups/code/{group_id}")
    
    # ==================== Attendance API (via /telegram) ====================
    
    async def get_group_attendance(
        self,
        group_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records for a group."""
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        result = await self._request(
            "GET",
            f"/api/v1/telegram/attendance/group/{group_id}",
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
            f"/api/v1/telegram/attendance/student/{student_id}",
            params=params
        )
        return result.get("items", []) if result else []
    
    async def get_recent_attendance_updates(
        self,
        group_id: int,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """Get attendance records updated since a specific time."""
        result = await self._request(
            "GET",
            f"/api/v1/telegram/attendance/group/{group_id}/updates",
            params={"since": since.isoformat()}
        )
        return result.get("items", []) if result else []
    
    # ==================== Subscription Check ====================

    async def check_bot_subscription(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Check if a group has active subscription with bot access.
        Bot access requires Plus or higher plan.
        """
        return await self._request(
            "GET",
            f"/api/v1/telegram/bot-check-subscription/{group_id}"
        )

    # ==================== Bot Specific API ====================
    
    async def register_telegram_chat(
        self,
        chat_id: int,
        group_code: str,
        chat_type: str,
        chat_title: Optional[str] = None
    ) -> bool:
        """Register Telegram chat for attendance notifications."""
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
        """Verify student identity for personal attendance access."""
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
