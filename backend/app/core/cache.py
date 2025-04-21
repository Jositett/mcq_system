"""
Simple in-memory caching system for the MCQ Test & Attendance System.
This module provides caching functionality without requiring external services like Redis.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Callable, Tuple, Union
from functools import wraps
import json
import hashlib

logger = logging.getLogger(__name__)


class LocalCache:
    """Simple thread-safe in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds for cache entries
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}  # {key: (value, expiry_time)}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry_time = self._cache[key]
            
            # Check if expired
            if expiry_time < time.time():
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (if None, use default_ttl)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expiry_time = time.time() + ttl
        
        with self._lock:
            self._cache[key] = (value, expiry_time)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def _cleanup_loop(self) -> None:
        """Background thread to clean up expired cache entries."""
        while True:
            time.sleep(60)  # Check every minute
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        with self._lock:
            # Find expired keys
            expired_keys = [
                key for key, (_, expiry_time) in self._cache.items()
                if expiry_time < current_time
            ]
            
            # Delete expired keys
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Create global cache instance
cache = LocalCache()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds (if None, use default_ttl)
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    key_parts.append(str(arg))
                else:
                    # For complex objects, use their string representation
                    key_parts.append(str(hash(str(arg))))
            
            # Sort kwargs for consistent keys
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if isinstance(v, (str, int, float, bool, type(None))):
                    key_parts.append(f"{k}:{v}")
                else:
                    # For complex objects, use their string representation
                    key_parts.append(f"{k}:{hash(str(v))}")
            
            # Create final key
            key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss for {key}, cached result")
            
            return result
        
        return wrapper
    
    return decorator


def async_cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache async function results.
    
    Args:
        ttl: Time-to-live in seconds (if None, use default_ttl)
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorated async function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    key_parts.append(str(arg))
                else:
                    # For complex objects, use their string representation
                    key_parts.append(str(hash(str(arg))))
            
            # Sort kwargs for consistent keys
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if isinstance(v, (str, int, float, bool, type(None))):
                    key_parts.append(f"{k}:{v}")
                else:
                    # For complex objects, use their string representation
                    key_parts.append(f"{k}:{hash(str(v))}")
            
            # Create final key
            key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss for {key}, cached result")
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache_key(key: str) -> None:
    """
    Invalidate a specific cache key.
    
    Args:
        key: Cache key to invalidate
    """
    cache.delete(key)


def invalidate_cache_prefix(prefix: str) -> None:
    """
    Invalidate all cache keys with a given prefix.
    
    Args:
        prefix: Prefix to match
    """
    with cache._lock:
        keys_to_delete = [
            key for key in cache._cache.keys()
            if key.startswith(prefix)
        ]
        
        for key in keys_to_delete:
            del cache._cache[key]
        
        if keys_to_delete:
            logger.debug(f"Invalidated {len(keys_to_delete)} cache keys with prefix '{prefix}'")


def clear_cache() -> None:
    """Clear the entire cache."""
    cache.clear()
    logger.debug("Cache cleared")
