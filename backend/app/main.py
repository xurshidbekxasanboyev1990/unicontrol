"""
UniControl Backend - Main Application Entry Point
==================================================
FastAPI application factory with middleware, routes, and event handlers.

Author: UniControl Team
Version: 1.0.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
from loguru import logger
import sys

from app.config import settings
from app.database import init_db, close_db
from app.core.exceptions import APIException
from app.api.v1 import api_router as api_v1_router
from app.api.mobile import mobile_router


# Configure Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

if settings.is_production:
    logger.add(
        "logs/unicontrol_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="gz",
        level="INFO"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Manages startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database (only in development)
    if settings.is_development:
        logger.info("Initializing database tables...")
        await init_db()
        logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="""
        UniControl - University Control System API
        
        ## Features
        - 🎓 Student Management
        - 👥 Group Management  
        - ✅ Attendance Tracking
        - 📊 Reports & Analytics
        - 📱 Mobile API
        - 🤖 AI Analysis
        - 📥 Excel Import/Export
        - 🔗 KUAF Mutoola Integration
        """,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # ====================
    # MIDDLEWARE
    # ====================
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Page-Size"]
    )
    
    # GZip Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Add X-Process-Time header to all responses."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        return response
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests."""
        logger.debug(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response
    
    # ====================
    # EXCEPTION HANDLERS
    # ====================
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom application exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "error_code": "API_ERROR"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.exception(f"Unexpected error: {exc}")
        
        if settings.DEBUG:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": str(exc),
                    "error_code": "INTERNAL_ERROR"
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Ichki server xatosi",
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    # ====================
    # ROUTES
    # ====================
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for load balancers."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    # API v1 routes (Web)
    app.include_router(
        api_v1_router,
        prefix="/api/v1",
        tags=["API v1"]
    )
    
    # Mobile API routes
    app.include_router(
        mobile_router,
        prefix="/api/mobile",
        tags=["Mobile API"]
    )
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )
