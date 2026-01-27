"""
UniControl - Schemas Package
============================
Pydantic schemas for request/response validation.

Author: UniControl Team
Version: 1.0.0
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
    UserLogin,
    Token,
    TokenPayload,
)
from app.schemas.student import (
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentImport,
    StudentListResponse,
)
from app.schemas.group import (
    GroupBase,
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupListResponse,
)
from app.schemas.attendance import (
    AttendanceBase,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceBatch,
    AttendanceReport,
)
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleListResponse,
)
from app.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationResponse,
    BroadcastNotificationCreate,
)
from app.schemas.report import (
    ReportBase,
    ReportCreate,
    ReportResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Student
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentImport",
    "StudentListResponse",
    # Group
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupResponse",
    "GroupListResponse",
    # Attendance
    "AttendanceBase",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "AttendanceBatch",
    "AttendanceReport",
    # Schedule
    "ScheduleBase",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleListResponse",
    # Notification
    "NotificationBase",
    "NotificationCreate",
    "NotificationResponse",
    "BroadcastNotificationCreate",
    # Report
    "ReportBase",
    "ReportCreate",
    "ReportResponse",
    "AIAnalysisRequest",
    "AIAnalysisResponse",
]