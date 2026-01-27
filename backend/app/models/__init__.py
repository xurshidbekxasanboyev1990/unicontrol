"""
UniControl - Database Models
============================
All SQLAlchemy models for the UniControl system.

Author: UniControl Team
Version: 1.0.0
"""

# Import all models here for Alembic to detect
from app.models.user import User, UserRole
from app.models.group import Group
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Schedule, WeekDay, ScheduleType
from app.models.notification import (
    Notification,
    BroadcastNotification,
    NotificationType,
    NotificationPriority,
)
from app.models.report import Report, ReportType, ReportFormat, ReportStatus
from app.models.mutoola import (
    MutoolaSync,
    MutoolaMapping,
    SyncType,
    SyncStatus,
    SyncDirection,
)
from app.models.activity_log import ActivityLog, ActivityAction

__all__ = [
    # User
    "User",
    "UserRole",
    # Group
    "Group",
    # Student
    "Student",
    # Attendance
    "Attendance",
    "AttendanceStatus",
    # Schedule
    "Schedule",
    "WeekDay",
    "ScheduleType",
    # Notification
    "Notification",
    "BroadcastNotification",
    "NotificationType",
    "NotificationPriority",
    # Report
    "Report",
    "ReportType",
    "ReportFormat",
    "ReportStatus",
    # Mutoola
    "MutoolaSync",
    "MutoolaMapping",
    "SyncType",
    "SyncStatus",
    "SyncDirection",
    # Activity Log
    "ActivityLog",
    "ActivityAction",
]
