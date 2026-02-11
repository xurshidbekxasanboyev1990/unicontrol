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
from app.models.file import File, Folder, FileType
from app.models.library import (
    Book,
    BookBorrow,
    BookReview,
    BookCategory,
    BookLanguage,
    BookStatus,
    BorrowStatus,
)
from app.models.canteen import (
    MenuCategory,
    MenuItem,
    Order,
    OrderItem,
    OrderStatus,
)
from app.models.club import Club, ClubMember
from app.models.subject import Subject, Direction, DirectionSubject
from app.models.tournament import Tournament, TournamentRegistration
from app.models.market import (
    UserMarketProfile,
    ServiceListing,
    MarketOrder as MarketOrderModel,
    EscrowTransaction,
    MarketDispute,
    MarketMessage,
    SellerPayout,
    MarketTariffPayment,
    MarketTariff,
    ListingStatus,
    ListingCategory,
    MarketOrderStatus,
    EscrowStatus,
    DisputeStatus,
    PayoutStatus,
)
from app.models.subscription import (
    SubscriptionPlan,
    GroupSubscription,
    SubscriptionPayment,
    SubscriptionSettings,
    SubscriptionPlanType,
    SubscriptionStatus,
    PaymentStatus,
)
from app.models.landing import LandingSettings

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
    # File Management
    "File",
    "Folder",
    "FileType",
    # Library
    "Book",
    "BookBorrow",
    "BookReview",
    "BookCategory",
    "BookLanguage",
    "BookStatus",
    "BorrowStatus",
    # Canteen
    "MenuCategory",
    "MenuItem",
    "Order",
    "OrderItem",
    "OrderStatus",
    # Club
    "Club",
    "ClubMember",
    # Subject & Direction
    "Subject",
    "Direction",
    "DirectionSubject",
    # Tournament
    "Tournament",
    "TournamentRegistration",
    # Market
    "UserMarketProfile",
    "ServiceListing",
    "MarketOrderModel",
    "EscrowTransaction",
    "MarketDispute",
    "MarketMessage",
    "SellerPayout",
    "MarketTariffPayment",
    "MarketTariff",
    "ListingStatus",
    "ListingCategory",
    "MarketOrderStatus",
    "EscrowStatus",
    "DisputeStatus",
    "PayoutStatus",
    # Subscription
    "SubscriptionPlan",
    "GroupSubscription",
    "SubscriptionPayment",
    "SubscriptionSettings",
    "SubscriptionPlanType",
    "SubscriptionStatus",
    "PaymentStatus",
    # Landing
    "LandingSettings",
]
