"""
API router for version 1 of the MCQ Test & Attendance System API.
This module aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api import auth, users, instructors, students, tests, attendance, face, uploads, health, admin

# Create API router for v1
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(instructors.router, prefix="/instructors", tags=["instructors"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(face.router, prefix="/face", tags=["face"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
