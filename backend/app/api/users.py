from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, get_async_db
from app.schemas.user import UserResponse, UserUpdate
from typing import List, Optional

router = APIRouter()

from app.services import user_service
from app.core.dependencies import require_role, get_current_user
from app.db import models
from fastapi import Depends, Path, Query
from pydantic import ValidationError
from app.services.file_storage_service import FileStorageService

@router.get(
    '/',
    response_model=List[UserResponse],
    tags=["Users"],
    summary="List all users",
    description="Returns a list of all users. Only accessible by admins.",
    responses={
        200: {"description": "List of users returned."},
        403: {"description": "Not authorized."}
    },
    response_description="List of users."
)
async def list_users(db: AsyncSession = Depends(get_async_db), current_user: models.User = Depends(require_role("admin"))):
    """List all users (admin only)."""
    users = await user_service.list_users_async(db)
    return users

from app.schemas.bulk_student import BulkStudentUploadRequest, BulkStudentUploadResponse
from app.services import student_service

@router.get(
    '/me',
    response_model=UserResponse,
    tags=["Users"],
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
    responses={
        200: {"description": "User profile returned."},
        401: {"description": "Not authenticated."}
    },
    response_description="Current user profile."
)
async def get_current_user_profile(db: AsyncSession = Depends(get_async_db), current_user: models.User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    # Refresh user data from database
    user = await user_service.get_user_async(db, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Add profile picture URL if it exists
    if user.profile_picture:
        user.profile_picture = FileStorageService.get_file_url(user.profile_picture)
        
    return user

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
async def get_user(
    user_id: int = Path(..., description="The ID of the user to get"), 
    db: AsyncSession = Depends(get_async_db), 
    current_user: models.User = Depends(require_role("admin"))
):
    """Get user by ID (admin only)."""
    user = await user_service.get_user_async(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Add profile picture URL if it exists
    if user.profile_picture:
        user.profile_picture = FileStorageService.get_file_url(user.profile_picture)
        
    return user

@router.put(
    '/{user_id}',
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user by ID",
    description="Update a user's information. Only accessible by admins.",
    responses={
        200: {"description": "User updated."},
        403: {"description": "Not authorized."},
        404: {"description": "User not found.", "content": {"application/json": {"example": {"detail": "User not found"}}}},
        422: {"description": "Validation error.", "content": {"application/json": {"example": {"detail": "Some validation error"}}}}
    },
    response_description="Updated user info."
)
async def update_user(
    update: UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    db: AsyncSession = Depends(get_async_db), 
    current_user: models.User = Depends(require_role("admin"))
):
    """Update user by ID (admin only)."""
    try:
        user = await user_service.update_user_async(db, user_id, update)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Add profile picture URL if it exists
        if user.profile_picture:
            user.profile_picture = FileStorageService.get_file_url(user.profile_picture)
            
        return user
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

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
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete"),
    db: AsyncSession = Depends(get_async_db), 
    current_user: models.User = Depends(require_role("admin"))
):
    """Delete user by ID (admin only)."""
    # Get user to check if they have a profile picture
    user = await user_service.get_user_async(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete profile picture if it exists
    if user.profile_picture:
        FileStorageService.delete_file(user.profile_picture)
    
    # Delete user
    success = await user_service.delete_user_async(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"detail": "User deleted"}

