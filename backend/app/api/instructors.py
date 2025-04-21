from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, get_async_db
from app.schemas.bulk_student import BulkStudentUploadRequest, BulkStudentUploadResponse
from app.schemas.bulk_question import BulkQuestionUploadRequest, BulkQuestionUploadResponse

router = APIRouter()

from app.services import instructor_service, student_service, test_service
from app.core.dependencies import require_role
from app.db import models
from fastapi import Depends, Path, Query

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
async def get_instructor_batches(
    instructor_id: int = Path(..., description="The ID of the instructor"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("instructor"))
):
    """Get batches managed by an instructor."""
    if current_user.id != instructor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructors can only access their own batches.")
    
    batches = await instructor_service.get_instructor_batches_async(db, instructor_id)
    
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
async def get_instructor_tests(
    instructor_id: int = Path(..., description="The ID of the instructor"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("instructor"))
):
    """Get tests managed by an instructor."""
    if current_user.id != instructor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructors can only access their own tests.")
    
    tests = await instructor_service.get_instructor_tests_async(db, instructor_id)
    
    return [
        {"id": t.id, "name": t.name, "batch_id": t.batch_id, "scheduled_at": t.scheduled_at} for t in tests
    ]

@router.post(
    '/{instructor_id}/batches/students/bulk',
    tags=["Instructors"],
    summary="Bulk add students to instructor batches",
    description="Bulk upload students to batches managed by this instructor.",
    response_model=BulkStudentUploadResponse,
    responses={
        200: {"description": "Bulk student upload results."},
        403: {"description": "Instructors can only upload to their own batches."}
    },
    response_description="Bulk student upload results."
)
async def bulk_add_students_instructor(
    req: BulkStudentUploadRequest,
    instructor_id: int = Path(..., description="The ID of the instructor"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("instructor"))
):
    """Bulk add students to instructor batches."""
    if not current_user.instructor or current_user.instructor.id != instructor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructors can only upload to their own batches.")
    
    results = await student_service.bulk_student_upload_async(db, req.students, instructor_id=instructor_id)
    
    return {"results": results}

@router.post(
    '/{instructor_id}/tests/questions/bulk',
    tags=["Instructors"],
    summary="Bulk add questions to instructor's tests",
    description="Bulk upload questions to tests managed by this instructor.",
    response_model=BulkQuestionUploadResponse,
    responses={
        200: {"description": "Bulk question upload results."},
        403: {"description": "Instructors can only upload to their own tests."}
    },
    response_description="Bulk question upload results."
)
async def bulk_add_questions_instructor(
    req: BulkQuestionUploadRequest,
    instructor_id: int = Path(..., description="The ID of the instructor"),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("instructor"))
):
    """Bulk add questions to instructor's tests."""
    if not current_user.instructor or current_user.instructor.id != instructor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructors can only upload to their own tests.")
    
    results = await test_service.bulk_question_upload_async(db, req.questions, instructor_id=instructor_id)
    
    return {"results": results}
