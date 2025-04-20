from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

from app.services import test_service
from app.schemas.test import TestCreate

from app.core.dependencies import require_role
from app.db import models

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
def create_test(test: TestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("instructor"))):
    """Create a new test (instructor only)."""
    db_test = test_service.create_test(db, test)
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
def list_tests(db: Session = Depends(get_db)):
    """List all tests."""
    tests = test_service.list_tests(db)
    return [
        {"id": t.id, "name": t.name, "batch_id": t.batch_id, "scheduled_at": t.scheduled_at} for t in tests
    ]

