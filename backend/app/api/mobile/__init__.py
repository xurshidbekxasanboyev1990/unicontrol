"""
UniControl - Mobile API Routes
==============================
Mobile application endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import APIRouter

from app.api.mobile import (
    auth,
    student,
    leader,
    push,
    general,
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

# Push Notifications
mobile_router.include_router(
    push.router,
    prefix="/push",
    tags=["Push Notifications"]
)

# General unprefixed mobile endpoints (legacy clients expect paths like /api/mobile/schedule)
mobile_router.include_router(
    general.router,
    prefix="",
    tags=["Mobile General"]
)
