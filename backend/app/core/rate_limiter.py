"""
UniControl - Rate Limiter Middleware
====================================
Redis-based rate limiting to prevent abuse.
Uses pure ASGI middleware to avoid BaseHTTPMiddleware issues.

Author: UniControl Team
Version: 1.1.0
"""

import json
from starlette.types import ASGIApp, Receive, Scope, Send
from loguru import logger

from app.config import settings
from app.database import get_redis


class RateLimitMiddleware:
    """
    Pure ASGI Redis-based rate limiter.
    Uses a sliding window counter per IP address.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Skip rate limiting for health checks, docs
        if path in ("/health", "/docs", "/redoc", "/openapi.json"):
            await self.app(scope, receive, send)
            return

        # Skip rate limiting for file upload/export endpoints
        skip_paths = ("/api/v1/contracts/import", "/api/v1/contracts/export")
        if any(path.startswith(sp) for sp in skip_paths):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        key = f"rate_limit:{client_ip}"

        try:
            redis = await get_redis()
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, 60)

            if current > settings.RATE_LIMIT_PER_MINUTE:
                ttl = await redis.ttl(key)
                logger.warning(
                    f"Rate limit exceeded for {client_ip}: {current} requests/min"
                )
                body = json.dumps({
                    "detail": "So'rovlar limiti oshib ketdi. Biroz kutib turing.",
                    "retry_after": ttl,
                }).encode("utf-8")
                await send({
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"retry-after", str(ttl).encode()],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": body,
                })
                return
        except Exception as e:
            logger.debug(f"Rate limiter Redis error (allowing request): {e}")

        await self.app(scope, receive, send)
