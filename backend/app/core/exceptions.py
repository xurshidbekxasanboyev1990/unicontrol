"""
UniControl - Custom Exceptions
==============================
Custom exception classes for API error handling.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class NotFoundException(APIException):
    """Resource not found exception."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class BadRequestException(APIException):
    """Bad request exception."""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class UnauthorizedException(APIException):
    """Unauthorized exception."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(APIException):
    """Forbidden exception."""
    
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ConflictException(APIException):
    """Conflict exception (e.g., duplicate resource)."""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ValidationException(APIException):
    """Validation error exception."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class ServiceUnavailableException(APIException):
    """Service unavailable exception."""
    
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class ExternalAPIException(APIException):
    """External API error exception."""
    
    def __init__(self, service: str, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service}: {detail}"
        )


class RateLimitException(APIException):
    """Rate limit exceeded exception."""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class FileException(APIException):
    """File handling exception."""
    
    def __init__(self, detail: str = "File operation error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
