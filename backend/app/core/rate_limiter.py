"""
UniControl - Rate Limiter Middleware
====================================
Redis-based rate limiting to prevent abuse.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.config import settings
from app.database import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple Redis-based rate limiter.
    Uses a sliding window counter per IP address.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks, docs, and heavy upload endpoints
        path = request.url.path
        if path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)
        
        # Skip rate limiting for file upload/export endpoints (they are slow by nature)
        skip_paths = ("/api/v1/contracts/import", "/api/v1/contracts/export")
        if any(path.startswith(sp) for sp in skip_paths):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        try:
            redis = await get_redis()
            current = await redis.incr(key)
            if current == 1:
                # Set TTL of 60 seconds on first request
                await redis.expire(key, 60)

            if current > settings.RATE_LIMIT_PER_MINUTE:
                ttl = await redis.ttl(key)
                logger.warning(
                    f"Rate limit exceeded for {client_ip}: {current} requests/min"
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "So'rovlar limiti oshib ketdi. Biroz kutib turing.",
                        "retry_after": ttl,
                    },
                    headers={"Retry-After": str(ttl)},
                )
        except Exception as e:
            # If Redis is unavailable, allow the request through
            logger.debug(f"Rate limiter Redis error (allowing request): {e}")

        return await call_next(request)
