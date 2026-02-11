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
from app.schemas.club import (
    ClubBase,
    ClubCreate,
    ClubUpdate,
    ClubResponse,
    ClubListResponse,
    ClubMemberCreate,
    ClubMemberResponse,
)
from app.schemas.subject import (
    SubjectBase,
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectListResponse,
    DirectionBase,
    DirectionCreate,
    DirectionUpdate,
    DirectionResponse,
    DirectionListResponse,
    DirectionSubjectUpdate,
)
from app.schemas.tournament import (
    TournamentBase,
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentListResponse,
    TournamentRegister,
    TournamentRegistrationResponse,
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
    # Club
    "ClubBase",
    "ClubCreate",
    "ClubUpdate",
    "ClubResponse",
    "ClubListResponse",
    "ClubMemberCreate",
    "ClubMemberResponse",
    # Subject
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "SubjectListResponse",
    # Direction
    "DirectionBase",
    "DirectionCreate",
    "DirectionUpdate",
    "DirectionResponse",
    "DirectionListResponse",
    "DirectionSubjectUpdate",
    # Tournament
    "TournamentBase",
    "TournamentCreate",
    "TournamentUpdate",
    "TournamentResponse",
    "TournamentListResponse",
    "TournamentRegister",
    "TournamentRegistrationResponse",
]