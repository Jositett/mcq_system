import os
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from typing import Callable
import traceback
import os

from app.api.v1.api import api_router as api_router_v1
from app.core.settings import settings
from app.db.init_db import init_db_async
from app.core.rate_limiter import RateLimitMiddleware
from app.core.docs import custom_openapi
from app.core.performance import PerformanceMonitoringMiddleware, get_performance_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Custom middleware for request timing and logging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log request details
            logger.info(
                f"Request: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
            return response
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            process_time = time.time() - start_time
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(e)}
            )

# Create FastAPI app with configuration
app = FastAPI(
    title="MCQ Test & Attendance System API",
    description="Backend API for MCQ-based test management and attendance tracking, supporting role-based access control for admins, instructors, and students.",
    version="1.0.0",
    contact={
        "name": "Support Team",
        "email": "support@example.com"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Set custom OpenAPI schema
app.openapi = lambda: custom_openapi(app)

# Startup event to run database migrations
from app.core.alembic_runner import run_alembic_upgrade

@app.on_event("startup")
async def startup_event():
    """Run Alembic migrations on startup in a thread pool."""
    import asyncio
    logger.info("Running startup tasks...")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, run_alembic_upgrade)
        logger.info("Alembic migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running Alembic migrations: {str(e)}")
        # Don't raise the exception to allow the app to start even if migrations fail
        # This is useful in development environments

# Root endpoint
@app.get("/", tags=["Info"])
def root():
    return {
        "message": "Welcome to the MCQ Test & Attendance System Backend API!",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "environment": settings.ENV,
        "version": "1.0.0"
    }

# Add middlewares

# 1. Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Performance monitoring middleware
app.add_middleware(
    PerformanceMonitoringMiddleware,
    exclude_paths=[
        "/docs", "/redoc", "/openapi.json",  # API documentation
        "/health", "/",  # Health checks and root
        "/static",  # Static files
    ]
)

# 4. Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,  # 100 requests per minute by default
    time_window=60,  # 60 seconds (1 minute)
    exclude_paths=[
        "/docs", "/redoc", "/openapi.json",  # API documentation
        "/health", "/",  # Health checks and root
        "/static",  # Static files
    ]
)

# 4. CORS middleware
origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers with versioning
api_prefix = settings.API_PREFIX

# v1 API
app.include_router(api_router_v1, prefix=f"{api_prefix}/v1")

# Default API (currently points to v1)
# This allows clients to use either /api/resource or /api/v1/resource
app.include_router(api_router_v1, prefix=f"{api_prefix}")

# Mount static files directory for uploads
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount(f"{api_prefix}/static/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
