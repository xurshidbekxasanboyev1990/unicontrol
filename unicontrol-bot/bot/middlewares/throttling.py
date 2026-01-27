from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from cachetools import TTLCache
import time


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware to prevent spam/flooding.
    Limits requests per user.
    """
    
    def __init__(self, rate_limit: float = 0.5, rate_limit_callback: float = 0.3):
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum seconds between messages
            rate_limit_callback: Minimum seconds between callbacks
        """
        self.rate_limit = rate_limit
        self.rate_limit_callback = rate_limit_callback
        self.cache = TTLCache(maxsize=10000, ttl=60)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user id
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            rate = self.rate_limit
            key_prefix = "msg"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            rate = self.rate_limit_callback
            key_prefix = "cb"
        else:
            return await handler(event, data)
        
        if not user_id:
            return await handler(event, data)
        
        # Check throttle
        cache_key = f"{key_prefix}:{user_id}"
        current_time = time.time()
        
        last_time = self.cache.get(cache_key, 0)
        
        if current_time - last_time < rate:
            # Throttled - skip handler
            if isinstance(event, CallbackQuery):
                await event.answer("Sekinroq! ⏳", show_alert=False)
            return None
        
        # Update cache and proceed
        self.cache[cache_key] = current_time
        return await handler(event, data)
