"""
UniControl - Core Package
=========================
Core utilities and helpers.

Author: UniControl Team
Version: 1.0.0
"""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
)
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_superadmin,
    require_admin,
    require_leader,
)
from app.core.exceptions import (
    APIException,
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
)

__all__ = [
    # Security
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "verify_password",
    "get_password_hash",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_superadmin",
    "require_admin",
    "require_leader",
    # Exceptions
    "APIException",
    "NotFoundException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
]