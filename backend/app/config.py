"""
UniControl Backend - Configuration Module
==========================================
Centralized configuration management using Pydantic Settings.
Supports environment variables and .env files.

Author: UniControl Team
Version: 1.0.0
"""

from functools import lru_cache
from typing import List, Optional
from datetime import datetime
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import pytz

# =====================
# TIMEZONE CONFIGURATION
# =====================
TIMEZONE_NAME = "Asia/Tashkent"
TASHKENT_TZ = pytz.timezone(TIMEZONE_NAME)


def now_tashkent() -> datetime:
    """Hozirgi vaqtni Asia/Tashkent timezone da qaytaradi."""
    return datetime.now(TASHKENT_TZ)


def today_tashkent():
    """Bugungi sanani Asia/Tashkent timezone da qaytaradi."""
    return datetime.now(TASHKENT_TZ).date()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All sensitive data should be stored in .env file (not committed to git).
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ====================
    # APP CONFIGURATION
    # ====================
    APP_NAME: str = "UniControl"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # ====================
    # SERVER
    # ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # ====================
    # DATABASE
    # ====================
    DATABASE_URL: str
    DATABASE_ECHO: bool = False  # SQL query logging
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # ====================
    # JWT AUTHENTICATION
    # ====================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ====================
    # CORS
    # ====================
    CORS_ORIGINS: str = 'http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000,http://192.168.213.3:5173,http://192.168.213.3:8000,http://192.168.213.3,https://unicontrol.uz,https://www.unicontrol.uz'
    CORS_ALLOW_CREDENTIALS: bool = True
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or return as-is if already a list."""
        if isinstance(v, str):
            return v
        return json.dumps(v)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list - supports both JSON and comma-separated."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            # If not JSON, split by comma
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # ====================
    # OPENAI API
    # ====================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # ====================
    # KUAF MUTOOLA API
    # ====================
    KUAF_API_BASE_URL: str = "https://api.mutoola.kuaf.uz/v1"
    KUAF_API_KEY: Optional[str] = None
    KUAF_API_SECRET: Optional[str] = None
    KUAF_SYNC_INTERVAL_MINUTES: int = 30
    
    # ====================
    # FIREBASE
    # ====================
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    
    # ====================
    # TELEGRAM BOT
    # ====================
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_WEBHOOK_SECRET: Optional[str] = None
    
    # ====================
    # REDIS
    # ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ====================
    # FILE STORAGE
    # ====================
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["xlsx", "xls", "csv", "pdf", "jpg", "jpeg", "png"]
    
    # ====================
    # RATE LIMITING
    # ====================
    RATE_LIMIT_PER_MINUTE: int = 200
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ====================
    # LOGGING
    # ====================
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # ====================
    # PAGINATION
    # ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every call.
    """
    return Settings()


# Global settings instance
settings = get_settings()
