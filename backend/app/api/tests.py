from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, get_async_db

router = APIRouter()

from app.services import test_service
from app.schemas.test import TestCreate

from app.core.dependencies import require_role, get_current_user
from app.db import models
from fastapi import Path, Query

from typing import List
from pydantic import BaseModel

class TestListRecord(BaseModel):
    id: int
    name: str
    batch_id: int
    scheduled_at: str | None = None

class TestCreateResponse(BaseModel):
    id: int
    name: str
    batch_id: int
    scheduled_at: str | None = None

@router.post(
    '/',
    tags=["Tests"],
    summary="Create a new test",
    description="Create a new test. Only accessible by instructors.",
    response_model=TestCreateResponse,
    responses={
        200: {"description": "Test created."},
        403: {"description": "Not authorized."}
    },
    response_description="Created test info."
)
async def create_test(
    test: TestCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("instructor"))
):
    """Create a new test (instructor only)."""
    # Check if instructor has access to the batch
    if current_user.role != "admin" and current_user.instructor:
        # Get instructor's batches
        batches = await test_service.instructor_service.get_instructor_batches_async(db, current_user.instructor.id)
        batch_ids = [batch.id for batch in batches]
        
        if test.batch_id not in batch_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create tests for your own batches"
            )
    
    db_test = await test_service.create_test_async(db, test)
    
    return TestCreateResponse(
        id=db_test.id,
        name=db_test.name,
        batch_id=db_test.batch_id,
        scheduled_at=db_test.scheduled_at
    )

@router.get(
    '/',
    tags=["Tests"],
    summary="List all tests",
    description="Returns a list of all tests.",
    response_model=List[TestListRecord],
    responses={
        200: {"description": "List of tests returned."}
    },
    response_description="List of tests."
)
async def list_tests(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all tests."""
    # For instructors, only show their own tests
    if current_user.role == "instructor" and current_user.instructor:
        tests = await test_service.instructor_service.get_instructor_tests_async(db, current_user.instructor.id)
    # For students, only show tests for their batch
    elif current_user.role == "student" and current_user.student:
        tests = await test_service.student_service.get_student_tests_async(db, current_user.student.id)
    # For admins, show all tests
    else:
        tests = await test_service.list_tests_async(db)
    
    return [
        {"id": t.id, "name": t.name, "batch_id": t.batch_id, "scheduled_at": t.scheduled_at} for t in tests
    ]

from app.schemas.bulk_question import BulkQuestionUploadRequest, BulkQuestionUploadResponse

@router.post(
    '/questions/bulk',
    tags=["Tests"],
    summary="Bulk add questions to the question pool (admin only)",
    description="Bulk upload questions to the question pool. Admin only.",
    response_model=BulkQuestionUploadResponse,
    responses={
        200: {"description": "Bulk question upload results."},
        403: {"description": "Admins only."}
    },
    response_description="Bulk question upload results."
)
async def bulk_add_questions_admin(
    req: BulkQuestionUploadRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Bulk add questions to the question pool (admin only)."""
    results = await test_service.bulk_question_upload_async(db, req.questions, instructor_id=None)
    return {"results": results}
