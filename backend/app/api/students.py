from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

from app.services import student_service

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
def get_student_tests(student_id: int, db: Session = Depends(get_db)):
    """Get tests assigned to a student."""
    tests = student_service.get_student_tests(db, student_id)
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
        404: {"description": "Student not found."}
    },
    response_description="List of attendance records."
)
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    """Get attendance records for a student."""
    attendance = student_service.get_student_attendance(db, student_id)
    return [
        {"id": a.id, "date": str(a.date), "status": a.status} for a in attendance
    ]

