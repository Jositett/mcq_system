"""
Rate limiting middleware for the MCQ Test & Attendance System API.
This module provides rate limiting functionality to protect the API from abuse.
"""

import time
from typing import Dict, Tuple, Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from app.core.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, rate_limit: int, time_window: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests: Dict[str, Tuple[int, float]] = {}  # {ip: (count, start_time)}
    
    def is_rate_limited(self, key: str) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Check if a key is rate limited.
        
        Args:
            key: The key to check (usually an IP address)
            
        Returns:
            Tuple of (is_limited, remaining_requests, retry_after)
        """
        current_time = time.time()
        
        # If key not in requests, add it
        if key not in self.requests:
            self.requests[key] = (1, current_time)
            return False, self.rate_limit - 1, None
        
        # Get current count and start time
        count, start_time = self.requests[key]
        
        # If time window has passed, reset count
        if current_time - start_time > self.time_window:
            self.requests[key] = (1, current_time)
            return False, self.rate_limit - 1, None
        
        # If count is less than rate limit, increment count
        if count < self.rate_limit:
            self.requests[key] = (count + 1, start_time)
            return False, self.rate_limit - count - 1, None
        
        # Calculate retry after
        retry_after = int(self.time_window - (current_time - start_time))
        
        # Rate limited
        return True, 0, retry_after
    
    def cleanup(self):
        """Clean up expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, start_time) in self.requests.items()
            if current_time - start_time > self.time_window
        ]
        for key in expired_keys:
            del self.requests[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = 100,
        time_window: int = 60,
        exclude_paths: Optional[list] = None,
        key_func: Optional[Callable[[Request], str]] = None,
    ):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: The ASGI app
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            exclude_paths: List of paths to exclude from rate limiting
            key_func: Function to extract the key from the request
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(rate_limit, time_window)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/health"]
        self.key_func = key_func or self._default_key_func
        
        # Start cleanup task
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # seconds
    
    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the request with rate limiting.
        
        Args:
            request: The request
            call_next: The next middleware
            
        Returns:
            The response
        """
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Clean up expired entries periodically
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.rate_limiter.cleanup()
            self._last_cleanup = current_time
        
        # Get key from request
        key = self.key_func(request)
        
        # Check if rate limited
        is_limited, remaining, retry_after = self.rate_limiter.is_rate_limited(key)
        
        # If rate limited, return 429 Too Many Requests
        if is_limited:
            logger.warning(f"Rate limited request from {key}")
            response = Response(
                content={"detail": "Too many requests"},
                status_code=429,
                media_type="application/json"
            )
            response.headers["Retry-After"] = str(retry_after)
            return response
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _default_key_func(self, request: Request) -> str:
        """
        Default function to extract the key from the request.
        Uses the client's IP address.
        
        Args:
            request: The request
            
        Returns:
            The key
        """
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get the first IP in the list (client IP)
            ip = forwarded.split(",")[0].strip()
        else:
            # Get the client IP from the request
            ip = request.client.host if request.client else "unknown"
        
        return ip
