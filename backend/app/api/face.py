from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db.session import get_db, get_async_db
from app.schemas.face import FaceImageCreate, FaceImageResponse, FaceVerification, FaceVerificationResponse
from app.services.face_service import FaceService
from app.core.dependencies import require_role, get_current_user
from app.db import models
from typing import List
import json

router = APIRouter(tags=["Facial Recognition"])

@router.post(
    "/upload",
    response_model=FaceImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a face image for training",
    description="Upload a base64-encoded face image for a user. The system will automatically extract the face embedding.",
    responses={
        201: {"description": "Face image uploaded successfully."},
        400: {"description": "Invalid image or no face detected."},
        401: {"description": "Not authenticated."},
        403: {"description": "Not authorized."}
    },
    response_description="Face image record with embedding."
)
async def upload_face_image(
    face_image: FaceImageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a face image for the current user."""
    # Only allow users to upload their own face images
    # Instructors and admins can upload for any user by specifying user_id
    user_id = current_user.id
    
    try:
        # Use our enhanced face service to handle the upload
        # It will automatically extract the face embedding
        db_face = await FaceService.create_face_image_async(db, user_id=user_id, face_data=face_image)
        return db_face
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error processing face image: {str(e)}"
        )

@router.get(
    "/my-images",
    response_model=List[FaceImageResponse],
    summary="Get all face images for the current user",
    description="Returns all face images uploaded by the current user.",
    responses={
        200: {"description": "List of face images."},
        401: {"description": "Not authenticated."}
    },
    response_description="List of face images."
)
async def get_my_face_images(
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all face images for the current user."""
    return await FaceService.get_user_face_images_async(db, user_id=current_user.id)

@router.post(
    "/verify",
    response_model=FaceVerificationResponse,
    summary="Verify a face against stored embeddings",
    description="Verify a face against stored embeddings. If user_id is provided, it will verify against that user's faces only.",
    responses={
        200: {"description": "Face verification result."},
        400: {"description": "Invalid image or no face detected."}
    },
    response_description="Face verification result."
)
async def verify_face(
    verification_data: FaceVerification,
    db: AsyncSession = Depends(get_async_db)
):
    """Verify a face against stored embeddings."""
    try:
        result = await FaceService.verify_face_async(db, verification_data)
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error verifying face: {str(e)}"
        )

@router.delete(
    "/{face_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a face image",
    description="Delete a face image by ID. Users can only delete their own face images.",
    responses={
        204: {"description": "Face image deleted."},
        401: {"description": "Not authenticated."},
        403: {"description": "Not authorized."},
        404: {"description": "Face image not found."}
    }
)
async def delete_face_image(
    face_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a face image by ID."""
    # Get the face image
    result = await db.execute(
        f"SELECT * FROM face_images WHERE id = {face_id}"
    )
    face_image = result.first()
    
    # Check if face image exists
    if not face_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face image not found"
        )
    
    # Check if user is authorized to delete this face image
    if face_image.user_id != current_user.id and current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this face image"
        )
    
    # Delete the face image
    success = await FaceService.delete_face_image_async(db, face_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face image not found"
        )
    
    return None

# For backward compatibility with sync clients
@router.post(
    "/upload/sync",
    response_model=FaceImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a face image for training (sync version)",
    description="Upload a base64-encoded face image for a user using synchronous API.",
    responses={
        201: {"description": "Face image uploaded successfully."},
        400: {"description": "Invalid image or no face detected."},
        401: {"description": "Not authenticated."},
        403: {"description": "Not authorized."}
    },
    response_description="Face image record with embedding.",
    deprecated=True
)
def upload_face_image_sync(
    face_image: FaceImageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a face image for the current user (sync version)."""
    # Only allow users to upload their own face images
    user_id = current_user.id
    
    try:
        # Use our face service to handle the upload
        db_face = FaceService.create_face_image(db, user_id=user_id, face_data=face_image)
        return db_face
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error processing face image: {str(e)}"
        )
