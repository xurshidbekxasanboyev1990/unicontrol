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
    teacher,
    dean,
    registrar,
    academic,
    push,
    general,
    dashboard,
    clubs,
    tournaments,
    reports,
    library,
    canteen,
    contracts,
    help,
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

# Teacher Mobile
mobile_router.include_router(
    teacher.router,
    prefix="/teacher",
    tags=["Mobile Teacher"]
)

# Dean Mobile
mobile_router.include_router(
    dean.router,
    prefix="/dean",
    tags=["Mobile Dean"]
)

# Registrar Mobile
mobile_router.include_router(
    registrar.router,
    prefix="/registrar",
    tags=["Mobile Registrar"]
)

# Academic Affairs Mobile
mobile_router.include_router(
    academic.router,
    prefix="/academic",
    tags=["Mobile Academic"]
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

# Library
mobile_router.include_router(
    library.router,
    prefix="/library",
    tags=["Mobile Library"]
)

# Canteen
mobile_router.include_router(
    canteen.router,
    prefix="/canteen",
    tags=["Mobile Canteen"]
)

# Contracts
mobile_router.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Mobile Contracts"]
)

# Help/FAQ
mobile_router.include_router(
    help.router,
    prefix="/help",
    tags=["Mobile Help"]
)

# General unprefixed mobile endpoints (schedule, attendance, groups, notifications/unread-count)
mobile_router.include_router(
    general.router,
    prefix="",
    tags=["Mobile General"]
)
