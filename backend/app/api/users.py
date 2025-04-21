from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserResponse

router = APIRouter()

from app.services import user_service
from app.schemas.user import UserUpdate
from app.core.dependencies import require_role
from app.db import models
from fastapi import Depends
from pydantic import ValidationError

@router.get(
    '/',
    response_model=list[UserResponse],
    tags=["Users"],
    summary="List all users",
    description="Returns a list of all users. Only accessible by admins.",
    responses={
        200: {"description": "List of users returned."},
        403: {"description": "Not authorized."}
    },
    response_description="List of users."
)
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(require_role("admin"))):
    """List all users (admin only)."""
    users = user_service.list_users(db)
    return users

from app.schemas.bulk_student import BulkStudentUploadRequest, BulkStudentUploadResponse
from app.services import student_service

@router.post(
    '/batches/students/bulk',
    tags=["Users"],
    summary="Bulk add students to any batch (admin only)",
    description="Bulk upload students to any batch. Admin only.",
    response_model=BulkStudentUploadResponse,
    responses={
        200: {"description": "Bulk student upload results."},
        403: {"description": "Admins only."}
    },
    response_description="Bulk student upload results."
)
def bulk_add_students_admin(
    req: BulkStudentUploadRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    results = student_service.bulk_student_upload(db, req.students, instructor_id=None)
    return {"results": results}

@router.get(
    '/{user_id}',
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by ID",
    description="Returns a user by user_id. Only accessible by admins.",
    responses={
        200: {"description": "User found."},
        403: {"description": "Not authorized."},
        404: {"description": "User not found.", "content": {"application/json": {"example": {"detail": "User not found"}}}}
    },
    response_description="User info."
)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("admin"))):
    """Get user by ID (admin only)."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put(
    '/{user_id}',
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user by ID",
    description="Update a user's full name or password. Only accessible by admins.",
    responses={
        200: {"description": "User updated."},
        403: {"description": "Not authorized."},
        404: {"description": "User not found.", "content": {"application/json": {"example": {"detail": "User not found"}}}},
        422: {"description": "Validation error.", "content": {"application/json": {"example": {"detail": "Some validation error"}}}}
    },
    response_description="Updated user info."
)
def update_user(user_id: int, update: UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("admin"))):
    """Update user by ID (admin only)."""
    try:
        user = user_service.update_user(db, user_id, full_name=update.full_name, password=update.password)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete(
    '/{user_id}',
    tags=["Users"],
    summary="Delete user by ID",
    description="Delete a user by user_id. Only accessible by admins.",
    responses={
        200: {"description": "User deleted.", "content": {"application/json": {"example": {"detail": "User deleted"}}}},
        403: {"description": "Not authorized."},
        404: {"description": "User not found.", "content": {"application/json": {"example": {"detail": "User not found"}}}}
    },
    response_description="User deleted confirmation."
)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("admin"))):
    """Delete user by ID (admin only)."""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

