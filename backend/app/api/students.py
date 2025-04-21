from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, get_async_db

router = APIRouter()

from app.services import student_service
from app.core.dependencies import get_current_user, require_role
from app.db import models
from fastapi import Path, Query

from typing import List
from pydantic import BaseModel

class StudentTestRecord(BaseModel):
    id: int
    name: str
    batch_id: int
    scheduled_at: str | None = None

class StudentAttendanceRecord(BaseModel):
    id: int
    date: str
    status: str

@router.get(
    '/{student_id}/tests',
    tags=["Students"],
    summary="Get tests assigned to a student",
    description="Returns a list of tests assigned to the specified student.",
    response_model=List[StudentTestRecord],
    responses={
        200: {"description": "List of tests returned."},
        404: {"description": "Student not found."}
    },
    response_description="List of tests."
)
async def get_student_tests(
    student_id: int = Path(..., description="The ID of the student"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get tests assigned to a student."""
    # Check if current user is admin, instructor, or the student themselves
    if current_user.role not in ["admin", "instructor"] and (
        not current_user.student or current_user.student.id != student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tests unless you are an admin or instructor"
        )
    
    tests = await student_service.get_student_tests_async(db, student_id)
    
    return [
        {"id": t.id, "name": t.name, "batch_id": t.batch_id, "scheduled_at": t.scheduled_at} for t in tests
    ]

@router.get(
    '/{student_id}/attendance',
    tags=["Students"],
    summary="Get attendance records for a student",
    description="Returns a list of attendance records for the specified student.",
    response_model=List[StudentAttendanceRecord],
    responses={
        200: {"description": "Attendance records returned."},
        404: {"description": "Student not found."},
        403: {"description": "Forbidden - you can only access your own attendance records unless you are an admin or instructor"}
    },
    response_description="List of attendance records."
)
async def get_student_attendance(
    student_id: int = Path(..., description="The ID of the student"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get attendance records for a student."""
    # Check if current user is admin, instructor, or the student themselves
    if current_user.role not in ["admin", "instructor"] and (
        not current_user.student or current_user.student.id != student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own attendance records unless you are an admin or instructor"
        )
    
    attendance = await student_service.get_student_attendance_async(db, student_id)
    
    return [
        {"id": a.id, "date": str(a.date), "status": a.status} for a in attendance
    ]

