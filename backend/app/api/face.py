from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.db.session import get_db
from app.schemas.face import FaceImageCreate, FaceImageResponse
from app.services.face_service import FaceService
from app.core.dependencies import require_role
from app.db import models
from typing import List
import face_recognition
import numpy as np
from PIL import Image
import io
import base64

router = APIRouter(tags=["Facial Recognition"])

@router.post(
    "/upload",
    response_model=FaceImageResponse,
    summary="Upload a face image for training",
    description="Upload a base64-encoded face image and optional embedding for a user. Only students can upload their own face images.",
    responses={
        200: {"description": "Face image uploaded."},
        403: {"description": "Not authorized."}
    },
    response_description="Face image record."
)
def upload_face_image(
    face_image: FaceImageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("student"))
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized.")
    try:
        # If embedding is provided by the client (JS), use it directly
        if face_image.embedding:
            # Validate embedding format (should be a JSON string or comma-separated floats)
            try:
                # Try parsing as JSON array
                import json
                emb = json.loads(face_image.embedding) if face_image.embedding.strip().startswith("[") else [float(x) for x in face_image.embedding.split(",")]
                if not isinstance(emb, list) or len(emb) < 10:
                    raise ValueError
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid embedding format.")
            # Save as comma-separated string for consistency
            face_image.embedding = ','.join(map(str, emb))
        else:
            # Fallback: extract embedding from image using backend
            image_data = face_image.image_data.split(',')[1] if ',' in face_image.image_data else face_image.image_data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image)
            face_locations = face_recognition.face_locations(image_array)
            if not face_locations:
                raise HTTPException(status_code=400, detail="No face detected in the image")
            if len(face_locations) > 1:
                raise HTTPException(status_code=400, detail="Multiple faces detected. Please upload an image with only one face.")
            face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
            face_image.embedding = ','.join(map(str, face_encoding))
        db_face = FaceService.create_face_image(db, user_id=current_user.id, face_data=face_image)
        return db_face
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/my-images",
    response_model=List[FaceImageResponse],
    summary="Get all face images for the current user",
    description="Returns all face images uploaded by the current user.",
    responses={200: {"description": "List of face images."}},
    response_description="List of face images."
)
def get_my_face_images(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("student"))
):
    return FaceService.get_user_face_images(db, user_id=current_user.id)
