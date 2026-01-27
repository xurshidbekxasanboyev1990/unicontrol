"""Handlers module"""

from .start import router as start_router
from .search import router as search_router
from .subscribe import router as subscribe_router
from .attendance import router as attendance_router
from .callbacks import router as callbacks_router
from .admin import router as admin_router

# List of all routers
routers = [
    admin_router,  # Admin router first for priority
    start_router,
    search_router,
    subscribe_router,
    attendance_router,
    callbacks_router
]

__all__ = [
    "start_router",
    "search_router",
    "subscribe_router",
    "attendance_router",
    "callbacks_router",
    "admin_router",
    "routers"
]
