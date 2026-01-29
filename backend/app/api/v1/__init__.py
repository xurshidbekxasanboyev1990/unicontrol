"""
UniControl - API v1 Routes
==========================
Web API routes.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    students,
    groups,
    attendance,
    schedule,
    notifications,
    reports,
    excel,
    ai,
    mutoola,
    dashboard,
    telegram,
    files,
    library,
    canteen,
)

api_router = APIRouter()

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Users
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Students
api_router.include_router(
    students.router,
    prefix="/students",
    tags=["Students"]
)

# Groups
api_router.include_router(
    groups.router,
    prefix="/groups",
    tags=["Groups"]
)

# Attendance
api_router.include_router(
    attendance.router,
    prefix="/attendance",
    tags=["Attendance"]
)

# Schedule
api_router.include_router(
    schedule.router,
    prefix="/schedule",
    tags=["Schedule"]
)

# Notifications
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

# Reports
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

# Excel Import/Export
api_router.include_router(
    excel.router,
    prefix="/excel",
    tags=["Excel"]
)

# AI Analysis
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Analysis"]
)

# Mutoola Integration
api_router.include_router(
    mutoola.router,
    prefix="/mutoola",
    tags=["Mutoola Integration"]
)

# Dashboard
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

# Telegram Bot Integration
api_router.include_router(
    telegram.router,
    tags=["Telegram Bot"]
)

# Files Management
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["Files"]
)

# Library (Books)
api_router.include_router(
    library.router,
    prefix="/library",
    tags=["Library"]
)

# Canteen (Oshxona)
api_router.include_router(
    canteen.router,
    prefix="/canteen",
    tags=["Canteen"]
)
