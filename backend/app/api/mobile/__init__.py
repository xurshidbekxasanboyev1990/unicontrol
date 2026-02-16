"""
UniControl - Mobile API Routes
==============================
Mobile application endpoints.

Author: UniControl Team
Version: 2.0.0
"""

from fastapi import APIRouter

from app.api.mobile import (
    auth,
    student,
    leader,
    push,
    general,
    dashboard,
    clubs,
    tournaments,
    reports,
)

mobile_router = APIRouter()

# Authentication
mobile_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Mobile Auth"]
)

# Student Mobile
mobile_router.include_router(
    student.router,
    prefix="/student",
    tags=["Mobile Student"]
)

# Leader Mobile
mobile_router.include_router(
    leader.router,
    prefix="/leader",
    tags=["Mobile Leader"]
)

# Dashboard (unified)
mobile_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Mobile Dashboard"]
)

# Clubs
mobile_router.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["Mobile Clubs"]
)

# Tournaments
mobile_router.include_router(
    tournaments.router,
    prefix="/tournaments",
    tags=["Mobile Tournaments"]
)

# Reports
mobile_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Mobile Reports"]
)

# Push Notifications
mobile_router.include_router(
    push.router,
    prefix="/push",
    tags=["Push Notifications"]
)

# General unprefixed mobile endpoints (schedule, attendance, groups, notifications/unread-count)
mobile_router.include_router(
    general.router,
    prefix="",
    tags=["Mobile General"]
)
