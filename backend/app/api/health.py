"""
Health check endpoints for the MCQ Test & Attendance System.
These endpoints provide information about the system's health and status.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import time
import os
import psutil
import platform
from typing import Dict, Any, List

from app.db.session import get_async_db
from app.core.settings import settings

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    summary="Basic health check",
    description="Returns a simple status to indicate the API is running.",
    response_description="Health status"
)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "environment": settings.ENV}


@router.get(
    "/detailed",
    summary="Detailed health check",
    description="Returns detailed health information about the system, including database connectivity.",
    response_description="Detailed health status"
)
async def detailed_health_check(db: AsyncSession = Depends(get_async_db)):
    """Detailed health check endpoint that tests database connectivity."""
    start_time = time.time()
    health_data = {
        "status": "ok",
        "environment": settings.ENV,
        "timestamp": start_time,
        "components": {}
    }
    
    # Check database
    try:
        # Test database connection with a simple query
        result = await db.execute(text("SELECT 1"))
        db_result = result.scalar()
        
        db_status = "ok" if db_result == 1 else "error"
        response_time = time.time() - start_time
        
        health_data["components"]["database"] = {
            "status": db_status,
            "response_time_ms": round(response_time * 1000, 2)
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_data["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Check file system
    try:
        # Check if upload directory is writable
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        
        test_file_path = os.path.join(upload_dir, ".health_check_test")
        with open(test_file_path, "w") as f:
            f.write("test")
        
        os.remove(test_file_path)
        
        health_data["components"]["file_system"] = {
            "status": "ok",
            "path": upload_dir
        }
    except Exception as e:
        logger.error(f"File system health check failed: {str(e)}")
        health_data["components"]["file_system"] = {
            "status": "error",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Add system information
    try:
        health_data["system"] = {
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
    except Exception as e:
        logger.error(f"System info collection failed: {str(e)}")
        health_data["system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Set response status code based on overall health
    response_status = status.HTTP_200_OK if health_data["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return health_data


@router.get(
    "/readiness",
    summary="Readiness check",
    description="Checks if the application is ready to serve requests.",
    response_description="Readiness status"
)
async def readiness_check(response: Response, db: AsyncSession = Depends(get_async_db)):
    """
    Readiness probe that checks if the application is ready to serve requests.
    This is useful for Kubernetes or other container orchestration systems.
    """
    is_ready = True
    checks = []
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        db_result = result.scalar()
        
        checks.append({
            "name": "database",
            "status": "ok" if db_result == 1 else "error"
        })
        
        if db_result != 1:
            is_ready = False
    except Exception as e:
        logger.error(f"Database readiness check failed: {str(e)}")
        checks.append({
            "name": "database",
            "status": "error",
            "error": str(e)
        })
        is_ready = False
    
    # Set response status code
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "ready": is_ready,
        "checks": checks
    }


@router.get(
    "/liveness",
    summary="Liveness check",
    description="Checks if the application is alive and running.",
    response_description="Liveness status"
)
async def liveness_check():
    """
    Liveness probe that checks if the application is alive.
    This is useful for Kubernetes or other container orchestration systems.
    """
    return {"alive": True, "timestamp": time.time()}
