from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, Index, JSON

from .base import Base


class Subscription(Base):
    """
    Telegram chat subscription to academic group attendance.
    Links Telegram group/chat with academic group code.
    """
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram chat info
    chat_id = Column(BigInteger, nullable=False, unique=True, index=True)
    chat_title = Column(String(255), nullable=True)
    chat_type = Column(String(50), nullable=False)  # private, group, supergroup
    
    # Academic group info
    group_code = Column(String(50), nullable=False, index=True)  # e.g., KI_25-09
    group_id = Column(Integer, nullable=True)  # API group ID
    group_name = Column(String(255), nullable=True)
    
    # Subscription settings
    is_active = Column(Boolean, default=True)
    notify_late = Column(Boolean, default=True)  # Notify when late
    notify_absent = Column(Boolean, default=True)  # Notify when absent
    notify_present = Column(Boolean, default=False)  # Notify when present
    
    # Metadata
    subscribed_by = Column(BigInteger, nullable=False)  # Telegram user ID
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_subscription_group_active", "group_code", "is_active"),
    )


class UserRegistration(Base):
    """
    Links Telegram user with UniControl student account.
    Allows personal attendance checking.
    """
    __tablename__ = "user_registrations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram user info
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    telegram_name = Column(String(255), nullable=True)
    
    # UniControl student info
    student_id = Column(Integer, nullable=True)  # API student ID
    student_name = Column(String(255), nullable=True)
    group_code = Column(String(50), nullable=True)
    
    # Registration status
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(10), nullable=True)
    
    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SentNotification(Base):
    """
    Tracks sent notifications to prevent duplicates.
    """
    __tablename__ = "sent_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Reference
    chat_id = Column(BigInteger, nullable=False, index=True)
    attendance_id = Column(Integer, nullable=False)  # API attendance record ID
    
    # Notification details
    student_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)  # present, late, absent
    
    # Metadata
    sent_at = Column(DateTime, default=datetime.utcnow)
    message_id = Column(Integer, nullable=True)  # Telegram message ID
    
    __table_args__ = (
        Index("ix_sent_notification_unique", "chat_id", "attendance_id", unique=True),
    )


class GroupCache(Base):
    """
    Cache for academic groups from API.
    Reduces API calls for group searches.
    """
    __tablename__ = "group_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Group info from API
    api_group_id = Column(Integer, nullable=False, unique=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    faculty = Column(String(255), nullable=True)
    course = Column(Integer, nullable=True)
    student_count = Column(Integer, nullable=True)
    
    # Cache metadata
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_group_cache_code", "code"),
    )


# ==================== ADMIN PANEL MODELS ====================

class BotUser(Base):
    """
    All bot users for statistics and broadcast.
    """
    __tablename__ = "bot_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram user info
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    
    # Status
    is_blocked = Column(Boolean, default=False)  # User blocked the bot
    is_banned = Column(Boolean, default=False)  # Admin banned user
    ban_reason = Column(String(500), nullable=True)
    
    # Metadata
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MandatoryChannel(Base):
    """
    Mandatory subscription channels.
    Users must subscribe to these channels to use the bot.
    """
    __tablename__ = "mandatory_channels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Channel info
    channel_id = Column(BigInteger, nullable=False, unique=True)
    channel_username = Column(String(100), nullable=True)  # @username
    channel_title = Column(String(255), nullable=False)
    channel_url = Column(String(255), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Display order
    
    # Metadata
    added_by = Column(BigInteger, nullable=False)  # Admin who added
    added_at = Column(DateTime, default=datetime.utcnow)


class BotSettings(Base):
    """
    Global bot settings.
    Single row table for bot configuration.
    """
    __tablename__ = "bot_settings"
    
    id = Column(Integer, primary_key=True, default=1)
    
    # Bot status
    is_active = Column(Boolean, default=True)  # Bot enabled/disabled
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    
    # Mandatory subscription
    force_subscribe = Column(Boolean, default=False)
    subscribe_message = Column(Text, nullable=True)
    
    # Welcome message
    welcome_message = Column(Text, nullable=True)
    
    # Notifications
    notifications_enabled = Column(Boolean, default=True)
    
    # Rate limits
    rate_limit_enabled = Column(Boolean, default=True)
    rate_limit_messages = Column(Integer, default=30)  # per minute
    
    # Extra settings as JSON
    extra_settings = Column(JSON, nullable=True)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, nullable=True)


class Broadcast(Base):
    """
    Broadcast/announcement messages.
    """
    __tablename__ = "broadcasts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Message content
    message_text = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, photo, video
    media_file_id = Column(String(255), nullable=True)
    
    # Buttons (JSON array)
    buttons = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, sending, completed, cancelled
    
    # Statistics
    total_users = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class AdminLog(Base):
    """
    Admin action logs.
    """
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Admin info
    admin_id = Column(BigInteger, nullable=False, index=True)
    admin_username = Column(String(100), nullable=True)
    
    # Action
    action = Column(String(100), nullable=False)  # e.g., "ban_user", "add_channel"
    action_details = Column(JSON, nullable=True)
    
    # Target (if applicable)
    target_type = Column(String(50), nullable=True)  # user, channel, broadcast
    target_id = Column(BigInteger, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

