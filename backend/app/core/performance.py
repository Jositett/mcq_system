"""
Performance monitoring middleware for the MCQ Test & Attendance System.
This module provides tools to track and analyze API performance.
"""

import time
import logging
from typing import Dict, List, Tuple, Optional, Callable
import statistics
import threading
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring for API endpoints."""
    
    def __init__(self, window_size: int = 100, log_interval: int = 60):
        """
        Initialize the performance monitor.
        
        Args:
            window_size: Number of requests to keep in the sliding window
            log_interval: Interval in seconds to log performance stats
        """
        self._routes: Dict[str, List[float]] = {}  # {route: [response_times]}
        self._lock = threading.RLock()
        self._window_size = window_size
        self._log_interval = log_interval
        self._last_log_time = time.time()
    
    def record_request(self, route: str, response_time: float) -> None:
        """
        Record a request's response time.
        
        Args:
            route: API route
            response_time: Response time in seconds
        """
        with self._lock:
            if route not in self._routes:
                self._routes[route] = []
            
            # Add response time to the route's list
            self._routes[route].append(response_time)
            
            # Trim list if it exceeds window size
            if len(self._routes[route]) > self._window_size:
                self._routes[route] = self._routes[route][-self._window_size:]
            
            # Log stats periodically
            current_time = time.time()
            if current_time - self._last_log_time > self._log_interval:
                self._log_stats()
                self._last_log_time = current_time
    
    def get_stats(self, route: Optional[str] = None) -> Dict:
        """
        Get performance statistics.
        
        Args:
            route: Optional route to get stats for (if None, get stats for all routes)
            
        Returns:
            Dictionary with performance statistics
        """
        with self._lock:
            if route:
                if route not in self._routes or not self._routes[route]:
                    return {"route": route, "requests": 0}
                
                return self._calculate_route_stats(route)
            
            # Get stats for all routes
            stats = {
                "total_routes": len(self._routes),
                "total_requests": sum(len(times) for times in self._routes.values()),
                "routes": []
            }
            
            # Calculate stats for each route
            for route in self._routes:
                if self._routes[route]:
                    route_stats = self._calculate_route_stats(route)
                    stats["routes"].append(route_stats)
            
            # Sort routes by average response time (descending)
            stats["routes"].sort(key=lambda x: x.get("avg_ms", 0), reverse=True)
            
            return stats
    
    def _calculate_route_stats(self, route: str) -> Dict:
        """
        Calculate statistics for a route.
        
        Args:
            route: API route
            
        Returns:
            Dictionary with route statistics
        """
        times = self._routes[route]
        
        if not times:
            return {"route": route, "requests": 0}
        
        # Convert to milliseconds for readability
        times_ms = [t * 1000 for t in times]
        
        return {
            "route": route,
            "requests": len(times),
            "avg_ms": round(statistics.mean(times_ms), 2),
            "median_ms": round(statistics.median(times_ms), 2),
            "min_ms": round(min(times_ms), 2),
            "max_ms": round(max(times_ms), 2),
            "p95_ms": round(self._percentile(times_ms, 95), 2),
            "p99_ms": round(self._percentile(times_ms, 99), 2)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        Calculate a percentile value from a list of data.
        
        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * percentile / 100
        
        if index.is_integer():
            return sorted_data[int(index)]
        
        # Interpolate between two values
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index
        
        return (1 - weight) * sorted_data[lower_index] + weight * sorted_data[upper_index]
    
    def _log_stats(self) -> None:
        """Log performance statistics."""
        stats = self.get_stats()
        
        logger.info(f"API Performance Stats - Total Routes: {stats['total_routes']}, "
                   f"Total Requests: {stats['total_requests']}")
        
        # Log the 5 slowest routes
        for i, route_stats in enumerate(stats["routes"][:5]):
            logger.info(f"Slow Route #{i+1}: {route_stats['route']} - "
                       f"Avg: {route_stats['avg_ms']}ms, "
                       f"P95: {route_stats['p95_ms']}ms, "
                       f"Requests: {route_stats['requests']}")
        
        # Save detailed stats to file periodically
        self._save_stats_to_file(stats)
    
    def _save_stats_to_file(self, stats: Dict) -> None:
        """
        Save performance statistics to a file.
        
        Args:
            stats: Performance statistics
        """
        try:
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Generate filename with current date
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"logs/performance_{today}.json"
            
            # Load existing stats if file exists
            existing_stats = []
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    try:
                        existing_stats = json.load(f)
                    except json.JSONDecodeError:
                        existing_stats = []
            
            # Add timestamp to stats
            timestamped_stats = {
                "timestamp": datetime.now().isoformat(),
                "stats": stats
            }
            
            # Append new stats
            existing_stats.append(timestamped_stats)
            
            # Write stats to file
            with open(filename, "w") as f:
                json.dump(existing_stats, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving performance stats to file: {str(e)}")


# Create global performance monitor
performance_monitor = PerformanceMonitor()


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance."""
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize the performance monitoring middleware.
        
        Args:
            app: The ASGI app
            exclude_paths: List of paths to exclude from monitoring
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/static"]
    
    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the request with performance monitoring.
        
        Args:
            request: The request
            call_next: The next middleware
            
        Returns:
            The response
        """
        # Skip monitoring for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Get route pattern
        route = self._get_route_pattern(request)
        
        # Record request timing
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Record in performance monitor
        performance_monitor.record_request(route, process_time)
        
        return response
    
    def _get_route_pattern(self, request: Request) -> str:
        """
        Get a normalized route pattern from a request.
        This converts paths like /users/123 to /users/{id} for better grouping.
        
        Args:
            request: The request
            
        Returns:
            Normalized route pattern
        """
        path = request.url.path
        method = request.method
        
        # Try to get the route pattern from the request scope
        if hasattr(request, "scope") and "route" in request.scope and hasattr(request.scope["route"], "path"):
            return f"{method} {request.scope['route'].path}"
        
        # Simple heuristic to normalize paths with IDs
        parts = path.split("/")
        normalized_parts = []
        
        for part in parts:
            # If part looks like an ID (numeric or UUID), replace with {id}
            if part.isdigit() or (len(part) > 20 and "-" in part):
                normalized_parts.append("{id}")
            else:
                normalized_parts.append(part)
        
        normalized_path = "/".join(normalized_parts)
        return f"{method} {normalized_path}"


def get_performance_stats(route: Optional[str] = None) -> Dict:
    """
    Get performance statistics.
    
    Args:
        route: Optional route to get stats for (if None, get stats for all routes)
        
    Returns:
        Dictionary with performance statistics
    """
    return performance_monitor.get_stats(route)
