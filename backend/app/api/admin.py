"""
Admin endpoints for the MCQ Test & Attendance System.
These endpoints provide administrative functionality for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any, List
import logging
import os
import platform
import psutil

from app.core.dependencies import require_role
from app.db import models
from app.core.performance import get_performance_stats

router = APIRouter(tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get(
    "/performance",
    summary="Get API performance statistics",
    description="Returns performance statistics for API endpoints. Admin only.",
    response_description="Performance statistics"
)
async def performance_statistics(
    route: Optional[str] = Query(None, description="Filter statistics by route"),
    current_user: models.User = Depends(require_role("admin"))
):
    """Get API performance statistics (admin only)."""
    return get_performance_stats(route)


@router.get(
    "/system-info",
    summary="Get system information",
    description="Returns information about the system running the application. Admin only.",
    response_description="System information"
)
async def system_info(current_user: models.User = Depends(require_role("admin"))):
    """Get system information (admin only)."""
    try:
        # Collect system information
        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
            "resources": {
                "cpu": {
                    "count": psutil.cpu_count(logical=False),
                    "logical_count": psutil.cpu_count(logical=True),
                    "usage_percent": psutil.cpu_percent(interval=0.1),
                },
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                    "used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                    "percent": psutil.disk_usage('/').percent,
                },
            },
            "process": {
                "pid": os.getpid(),
                "memory_usage_mb": round(psutil.Process(os.getpid()).memory_info().rss / (1024**2), 2),
                "cpu_usage_percent": psutil.Process(os.getpid()).cpu_percent(interval=0.1),
                "threads": psutil.Process(os.getpid()).num_threads(),
                "uptime_seconds": round(time.time() - psutil.Process(os.getpid()).create_time(), 2),
            }
        }
        
        return info
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system info: {str(e)}"
        )


@router.get(
    "/logs",
    summary="Get application logs",
    description="Returns recent application logs. Admin only.",
    response_description="Application logs"
)
async def get_logs(
    lines: int = Query(100, description="Number of lines to return", ge=1, le=1000),
    current_user: models.User = Depends(require_role("admin"))
):
    """Get application logs (admin only)."""
    try:
        # Check if logs directory exists
        if not os.path.exists("logs"):
            return {"logs": [], "message": "No logs directory found"}
        
        # Get list of log files
        log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
        
        if not log_files:
            return {"logs": [], "message": "No log files found"}
        
        # Sort log files by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join("logs", x)), reverse=True)
        
        # Read the most recent log file
        latest_log = os.path.join("logs", log_files[0])
        
        with open(latest_log, "r") as f:
            # Read the last N lines
            log_lines = f.readlines()[-lines:]
        
        return {
            "file": latest_log,
            "lines": lines,
            "logs": log_lines
        }
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting logs: {str(e)}"
        )


import time

@router.post(
    "/clear-cache",
    summary="Clear application cache",
    description="Clears the application's in-memory cache. Admin only.",
    response_description="Cache clear result"
)
async def clear_cache(current_user: models.User = Depends(require_role("admin"))):
    """Clear application cache (admin only)."""
    try:
        from app.core.cache import clear_cache
        
        # Record time before clearing cache
        start_time = time.time()
        
        # Clear cache
        clear_cache()
        
        # Calculate time taken
        time_taken = time.time() - start_time
        
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "time_taken_ms": round(time_taken * 1000, 2)
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )
