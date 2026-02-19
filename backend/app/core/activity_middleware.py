"""
Activity Logging Middleware
===========================
Automatically logs all API requests to ActivityLog.
Tracks every user action: page views, data access, mutations.
Excludes health checks, static files, and docs endpoints.
"""

import json
import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import select
from app.database import async_session_maker
from app.models.activity_log import ActivityLog, ActivityAction
from app.models.user import User
from app.config import TASHKENT_TZ
from datetime import datetime
import logging
import jwt
from app.config import settings

logger = logging.getLogger(__name__)

# Paths to skip logging
SKIP_PATHS = {
    "/health", "/docs", "/redoc", "/openapi.json",
    "/api/v1/logs", "/api/logs",  # Don't log viewing logs
}

SKIP_PREFIXES = ("/static/", "/assets/", "/favicon")

# Map HTTP methods to actions
METHOD_ACTION_MAP = {
    "GET": ActivityAction.READ,
    "POST": ActivityAction.CREATE,
    "PUT": ActivityAction.UPDATE,
    "PATCH": ActivityAction.UPDATE,
    "DELETE": ActivityAction.DELETE,
}

# Describe endpoints for human-readable logs
ENDPOINT_DESCRIPTIONS = {
    # Auth
    ("POST", "/auth/login"): "Tizimga kirdi",
    ("POST", "/auth/logout"): "Tizimdan chiqdi",
    ("POST", "/auth/change-password"): "Parolni o'zgartirdi",
    # Students
    ("GET", "/students"): "Talabalar ro'yxatini ko'rdi",
    ("GET", "/students/"): "Talaba ma'lumotini ko'rdi",
    ("POST", "/students"): "Yangi talaba qo'shdi",
    ("PUT", "/students/"): "Talaba ma'lumotini yangiladi",
    ("DELETE", "/students/"): "Talabani o'chirdi",
    # Groups
    ("GET", "/groups"): "Guruhlar ro'yxatini ko'rdi",
    ("POST", "/groups"): "Yangi guruh yaratdi",
    # Attendance
    ("GET", "/attendance"): "Davomat ma'lumotini ko'rdi",
    ("POST", "/attendance"): "Davomat belgiladi",
    # Schedule
    ("GET", "/schedules"): "Jadval ko'rdi",
    ("POST", "/schedules"): "Jadval yaratdi",
    ("PUT", "/schedules/"): "Jadvalni yangiladi",
    ("DELETE", "/schedules/"): "Jadvalni o'chirdi",
    # Users
    ("GET", "/users"): "Foydalanuvchilar ro'yxatini ko'rdi",
    ("POST", "/users"): "Yangi foydalanuvchi yaratdi",
    ("PUT", "/users/"): "Foydalanuvchini yangiladi",
    ("DELETE", "/users/"): "Foydalanuvchini o'chirdi",
    # Reports
    ("GET", "/reports"): "Hisobotlar ro'yxatini ko'rdi",
    ("POST", "/reports"): "Hisobot yaratdi",
    # Workload
    ("GET", "/teacher/workload"): "O'qituvchi bandligini ko'rdi",
    ("GET", "/teacher/workload/my"): "O'z bandligini ko'rdi",
    ("GET", "/teacher/workload/teachers"): "O'qituvchilar ro'yxatini ko'rdi (bandlik)",
    ("POST", "/academic/workload/import"): "Bandlik ma'lumotlarini import qildi",
    # AI
    ("POST", "/academic/ai-generate"): "AI jadval generatsiya qildi",
    # Notifications
    ("GET", "/notifications"): "Bildirishnomalarni ko'rdi",
    ("POST", "/notifications"): "Bildirishnoma yubordi",
    # Import
    ("POST", "/import"): "Ma'lumot import qildi",
    # Contracts
    ("GET", "/contracts"): "Shartnomalarni ko'rdi",
    # Subjects
    ("GET", "/subjects"): "Fanlar ro'yxatini ko'rdi",
    # Market
    ("GET", "/market"): "Market sahifasini ko'rdi",
    # Profile
    ("GET", "/auth/me"): "Profilini ko'rdi",
    ("PUT", "/auth/profile"): "Profilini yangiladi",
}


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _extract_user_id(request: Request) -> Optional[int]:
    """Try to extract user_id from JWT token in Authorization header."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub") or payload.get("user_id")
    except Exception:
        return None


def _get_description(method: str, path: str) -> str:
    """Get human-readable description for the endpoint."""
    # Strip API prefix
    clean_path = path
    for prefix in ("/api/v1/", "/api/"):
        if path.startswith(prefix):
            clean_path = path[len(prefix) - 1:]
            break

    # Exact match
    key = (method, clean_path)
    if key in ENDPOINT_DESCRIPTIONS:
        return ENDPOINT_DESCRIPTIONS[key]

    # Prefix match (for /students/123 etc.)
    for (m, p), desc in ENDPOINT_DESCRIPTIONS.items():
        if m == method and p.endswith("/") and clean_path.startswith(p):
            return desc

    # Generic
    return f"{method} {clean_path}"


def _get_entity_type(path: str) -> Optional[str]:
    """Extract entity type from path."""
    clean = path
    for prefix in ("/api/v1/", "/api/"):
        if path.startswith(prefix):
            clean = path[len(prefix):]
            break
    parts = clean.split("/")
    if parts:
        return parts[0]
    return None


def _should_skip(path: str, method: str) -> bool:
    """Check if this request should be skipped."""
    if path in SKIP_PATHS:
        return True
    for prefix in SKIP_PREFIXES:
        if path.startswith(prefix):
            return True
    # Skip OPTIONS (CORS preflight)
    if method == "OPTIONS":
        return True
    return False


class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _should_skip(request.url.path, request.method):
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Only log for authenticated API requests
        user_id = _extract_user_id(request)
        if user_id is None:
            return response

        # Don't log super/academic viewing logs endpoint
        path = request.url.path
        if "/logs" in path and request.method == "GET":
            return response

        try:
            action = METHOD_ACTION_MAP.get(request.method, ActivityAction.SYSTEM)
            description = _get_description(request.method, path)
            entity_type = _get_entity_type(path)
            ip = _get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")[:500]

            context_data = {
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "query_params": str(request.query_params) if request.query_params else None,
            }

            async with async_session_maker() as session:
                log_entry = ActivityLog(
                    user_id=int(user_id),
                    action=action,
                    description=description,
                    entity_type=entity_type,
                    ip_address=ip,
                    user_agent=user_agent,
                    context=json.dumps(context_data, default=str, ensure_ascii=False),
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Activity logging failed: {e}")

        return response
