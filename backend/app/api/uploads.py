"""
API endpoints for file uploads in the MCQ Test & Attendance System.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Optional, List

from app.db.session import get_db, get_async_db
from app.core.dependencies import get_current_user
from app.db import models
from app.services.file_storage_service import FileStorageService

router = APIRouter(tags=["Uploads"])


@router.post(
    "/profile-picture",
    summary="Upload a profile picture",
    description="Upload a profile picture for the current user.",
    responses={
        200: {"description": "Profile picture uploaded successfully."},
        400: {"description": "Invalid file format or size."},
        401: {"description": "Not authenticated."}
    }
)
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a profile picture for the current user."""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Save the file
        file_path = await FileStorageService.save_upload_file(
            file,
            subdir="profile_pictures",
            max_size_mb=2.0,
            allowed_types=allowed_types
        )
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            FileStorageService.delete_file(current_user.profile_picture)
        
        # Update user's profile picture
        stmt = (
            update(models.User)
            .where(models.User.id == current_user.id)
            .values(profile_picture=file_path)
        )
        await db.execute(stmt)
        await db.commit()
        
        # Get file URL
        file_url = FileStorageService.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "message": "Profile picture uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading profile picture: {str(e)}"
        )


@router.post(
    "/profile-picture/base64",
    summary="Upload a profile picture using base64",
    description="Upload a base64-encoded profile picture for the current user.",
    responses={
        200: {"description": "Profile picture uploaded successfully."},
        400: {"description": "Invalid base64 data."},
        401: {"description": "Not authenticated."}
    }
)
async def upload_profile_picture_base64(
    base64_data: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a base64-encoded profile picture for the current user."""
    try:
        # Save the file
        file_path = FileStorageService.save_base64_image(
            base64_data,
            subdir="profile_pictures",
            max_size_mb=2.0
        )
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            FileStorageService.delete_file(current_user.profile_picture)
        
        # Update user's profile picture
        stmt = (
            update(models.User)
            .where(models.User.id == current_user.id)
            .values(profile_picture=file_path)
        )
        await db.execute(stmt)
        await db.commit()
        
        # Get file URL
        file_url = FileStorageService.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "message": "Profile picture uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading profile picture: {str(e)}"
        )


@router.delete(
    "/profile-picture",
    summary="Delete profile picture",
    description="Delete the current user's profile picture.",
    responses={
        200: {"description": "Profile picture deleted successfully."},
        401: {"description": "Not authenticated."},
        404: {"description": "Profile picture not found."}
    }
)
async def delete_profile_picture(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete the current user's profile picture."""
    try:
        # Check if user has a profile picture
        if not current_user.profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No profile picture found"
            )
        
        # Delete the file
        success = FileStorageService.delete_file(current_user.profile_picture)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture file not found"
            )
        
        # Update user's profile picture to null
        stmt = (
            update(models.User)
            .where(models.User.id == current_user.id)
            .values(profile_picture=None)
        )
        await db.execute(stmt)
        await db.commit()
        
        return {
            "success": True,
            "message": "Profile picture deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile picture: {str(e)}"
        )


# For backward compatibility with sync clients
@router.post(
    "/profile-picture/sync",
    summary="Upload a profile picture (sync version)",
    description="Upload a profile picture for the current user using synchronous API.",
    responses={
        200: {"description": "Profile picture uploaded successfully."},
        400: {"description": "Invalid file format or size."},
        401: {"description": "Not authenticated."}
    },
    deprecated=True
)
def upload_profile_picture_sync(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a profile picture for the current user (sync version)."""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content
        file_content = file.file.read()
        
        # Create UploadFile with read content for async function
        upload_file = UploadFile(
            filename=file.filename,
            content_type=file.content_type,
            file=None
        )
        
        # Save the file using sync method
        # Note: This is a simplified version for backward compatibility
        # In a real implementation, you would have a sync version of save_upload_file
        file_path = FileStorageService.save_base64_image(
            base64.b64encode(file_content).decode('utf-8'),
            subdir="profile_pictures",
            max_size_mb=2.0
        )
        
        # Delete old profile picture if exists
        if current_user.profile_picture:
            FileStorageService.delete_file(current_user.profile_picture)
        
        # Update user's profile picture
        current_user.profile_picture = file_path
        db.commit()
        
        # Get file URL
        file_url = FileStorageService.get_file_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "message": "Profile picture uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading profile picture: {str(e)}"
        )
