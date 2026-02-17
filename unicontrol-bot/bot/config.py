from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List
from datetime import datetime
import pytz
import json

# Timezone helpers
TIMEZONE_NAME = "Asia/Tashkent"
TASHKENT_TZ = pytz.timezone(TIMEZONE_NAME)

def now_tashkent():
    """Get current datetime in Tashkent timezone."""
    return datetime.now(TASHKENT_TZ)

def today_tashkent():
    """Get current date in Tashkent timezone."""
    return datetime.now(TASHKENT_TZ).date()


class Settings(BaseSettings):
    """Bot configuration settings"""
    
    # Telegram Bot
    bot_token: str = Field(..., env="BOT_TOKEN")
    
    # UniControl API
    api_base_url: str = Field(default="http://localhost:8000/api/v1", env="API_BASE_URL")
    api_key: str = Field(default="", env="API_KEY")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./bot.db", 
        env="DATABASE_URL"
    )
    
    # Bot settings - Admin IDs (comma-separated in .env)
    admin_ids: str = Field(default="", env="ADMIN_IDS")
    
    # Scheduler settings
    attendance_check_interval: int = Field(default=300)  # 5 minutes
    
    # Rate limiting
    rate_limit: int = Field(default=1)  # requests per second
    rate_limit_period: int = Field(default=1)  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        if not self.admin_ids:
            return []
        try:
            return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]
        except:
            return []


# Create settings instance
_settings = Settings()

# Wrapper class with admin_ids as list
class SettingsWrapper:
    def __init__(self, settings: Settings):
        self._settings = settings
    
    def __getattr__(self, name):
        if name == "admin_ids":
            return self._settings.admin_ids_list
        return getattr(self._settings, name)

settings = SettingsWrapper(_settings)
