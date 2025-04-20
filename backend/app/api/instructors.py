from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

from app.services import instructor_service
from app.core.dependencies import require_role
from app.db import models
from fastapi import Depends

from typing import List
from pydantic import BaseModel

class InstructorBatchRecord(BaseModel):
    id: int
    name: str
    instructor_id: int

class InstructorTestRecord(BaseModel):
    id: int
    name: str
    batch_id: int
    scheduled_at: str | None = None

@router.get(
    '/{instructor_id}/batches',
    tags=["Instructors"],
    summary="Get batches managed by an instructor",
    description="Returns a list of batches managed by the specified instructor.",
    response_model=List[InstructorBatchRecord],
    responses={
        200: {"description": "List of batches returned."},
        403: {"description": "Instructors can only access their own batches."}
    },
    response_description="List of batches."
)
def get_instructor_batches(instructor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("instructor"))):
    """Get batches managed by an instructor."""
    if current_user.id != instructor_id:
        raise HTTPException(status_code=403, detail="Instructors can only access their own batches.")
    batches = instructor_service.get_instructor_batches(db, instructor_id)
    return [
        {"id": b.id, "name": b.name, "instructor_id": b.instructor_id} for b in batches
    ]

@router.get(
    '/{instructor_id}/tests',
    tags=["Instructors"],
    summary="Get tests managed by an instructor",
    description="Returns a list of tests managed by the specified instructor.",
    response_model=List[InstructorTestRecord],
    responses={
        200: {"description": "List of tests returned."},
        403: {"description": "Instructors can only access their own tests."}
    },
    response_description="List of tests."
)
def get_instructor_tests(instructor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("instructor"))):
    """Get tests managed by an instructor."""
    if current_user.id != instructor_id:
        raise HTTPException(status_code=403, detail="Instructors can only access their own tests.")
    tests = instructor_service.get_instructor_tests(db, instructor_id)
    return [
        {"id": t.id, "name": t.name, "batch_id": t.batch_id, "scheduled_at": t.scheduled_at} for t in tests
    ]

