import base64
import json
import numpy as np
import face_recognition
from io import BytesIO
from PIL import Image
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db import models
from app.schemas.face import FaceImageCreate, FaceVerification
from app.core.settings import settings


class FaceService:
    # Similarity threshold for face matching (lower = more strict)
    SIMILARITY_THRESHOLD = 0.6
    
    @staticmethod
    def _decode_base64_image(base64_string: str) -> np.ndarray:
        """Decode a base64 image string to a numpy array for face_recognition."""
        try:
            # Remove potential data URL prefix
            if ',' in base64_string:
                base64_string = base64_string.split(',', 1)[1]
                
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Open as PIL Image
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed (face_recognition requires RGB)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Convert to numpy array
            return np.array(image)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image format: {str(e)}"
            )
    
    @staticmethod
    def _extract_face_embedding(image_array: np.ndarray) -> Optional[List[float]]:
        """Extract face embedding from image array."""
        # Detect faces in the image
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            return None
            
        # Get face encodings (embeddings)
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        
        if not face_encodings:
            return None
            
        # Return the first face encoding as a list
        return face_encodings[0].tolist()
    
    @staticmethod
    async def create_face_image_async(db: AsyncSession, user_id: int, face_data: FaceImageCreate) -> models.FaceImage:
        """Create a new face image record with embedding using async SQLAlchemy."""
        # Decode the base64 image
        image_array = FaceService._decode_base64_image(face_data.image_data)
        
        # Extract face embedding
        embedding = FaceService._extract_face_embedding(image_array)
        
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
        
        # Store embedding as JSON string
        embedding_json = json.dumps(embedding)
        
        # Create database record
        db_face = models.FaceImage(
            user_id=user_id,
            image_data=face_data.image_data,  # Store original base64 image
            embedding=embedding_json,
            created_at=face_data.created_at or datetime.now().date()
        )
        
        db.add(db_face)
        await db.commit()
        await db.refresh(db_face)
        
        return db_face
    
    @staticmethod
    async def get_user_face_images_async(db: AsyncSession, user_id: int) -> List[models.FaceImage]:
        """Get all face images for a specific user using async SQLAlchemy."""
        result = await db.execute(
            select(models.FaceImage).where(models.FaceImage.user_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_face_images_async(db: AsyncSession) -> List[models.FaceImage]:
        """Get all face images in the database using async SQLAlchemy."""
        result = await db.execute(select(models.FaceImage))
        return result.scalars().all()
    
    @staticmethod
    async def verify_face_async(db: AsyncSession, verification_data: FaceVerification) -> Dict[str, Any]:
        """Verify a face against stored embeddings using async SQLAlchemy."""
        # Decode the image and extract embedding
        image_array = FaceService._decode_base64_image(verification_data.image_data)
        new_embedding = FaceService._extract_face_embedding(image_array)
        
        if not new_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the verification image"
            )
        
        # Convert to numpy array for comparison
        new_embedding_array = np.array(new_embedding)
        
        # Get user to verify against (if specified)
        if verification_data.user_id:
            # Get face images for specific user
            face_images = await FaceService.get_user_face_images_async(db, verification_data.user_id)
            if not face_images:
                return {
                    "verified": False,
                    "message": "No reference faces found for this user"
                }
        else:
            # Get all face images (for identification)
            face_images = await FaceService.get_all_face_images_async(db)
            if not face_images:
                return {
                    "verified": False,
                    "message": "No reference faces found in the system"
                }
        
        # Find best match
        best_match = FaceService._find_best_match(new_embedding_array, face_images)
        
        if best_match:
            user_id, similarity = best_match
            
            # Get user details
            result = await db.execute(select(models.User).where(models.User.id == user_id))
            user = result.scalars().first()
            
            return {
                "verified": True,
                "user_id": user_id,
                "similarity": similarity,
                "username": user.username if user else None,
                "full_name": user.full_name if user else None
            }
        
        return {
            "verified": False,
            "message": "No matching face found"
        }
    
    @staticmethod
    def _find_best_match(embedding: np.ndarray, face_images: List[models.FaceImage]) -> Optional[Tuple[int, float]]:
        """Find the best matching face from a list of face images."""
        best_similarity = 0
        best_user_id = None
        
        for face_image in face_images:
            # Parse stored embedding from JSON
            stored_embedding = json.loads(face_image.embedding)
            stored_embedding_array = np.array(stored_embedding)
            
            # Calculate face distance (lower is more similar)
            face_distance = face_recognition.face_distance([stored_embedding_array], embedding)[0]
            
            # Convert distance to similarity (1 - distance)
            similarity = 1 - face_distance
            
            # Update best match if this is better
            if similarity > best_similarity and similarity > FaceService.SIMILARITY_THRESHOLD:
                best_similarity = similarity
                best_user_id = face_image.user_id
        
        if best_user_id:
            return (best_user_id, float(best_similarity))
        
        return None
    
    @staticmethod
    async def delete_face_image_async(db: AsyncSession, face_id: int) -> bool:
        """Delete a face image by ID using async SQLAlchemy."""
        result = await db.execute(
            select(models.FaceImage).where(models.FaceImage.id == face_id)
        )
        face_image = result.scalars().first()
        
        if not face_image:
            return False
            
        await db.delete(face_image)
        await db.commit()
        
        return True
    
    # Sync methods (for backward compatibility)
    @staticmethod
    def create_face_image(db: Session, user_id: int, face_data: FaceImageCreate) -> models.FaceImage:
        """Create a new face image record with embedding (sync version for backward compatibility)."""
        # Decode the base64 image
        image_array = FaceService._decode_base64_image(face_data.image_data)
        
        # Extract face embedding
        embedding = FaceService._extract_face_embedding(image_array)
        
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
        
        # Store embedding as JSON string
        embedding_json = json.dumps(embedding)
        
        # Create database record
        db_face = models.FaceImage(
            user_id=user_id,
            image_data=face_data.image_data,  # Store original base64 image
            embedding=embedding_json,
            created_at=face_data.created_at or datetime.now().date()
        )
        
        db.add(db_face)
        db.commit()
        db.refresh(db_face)
        
        return db_face
    
    @staticmethod
    def get_user_face_images(db: Session, user_id: int) -> List[models.FaceImage]:
        """Get all face images for a specific user (sync version for backward compatibility)."""
        return db.query(models.FaceImage).filter(models.FaceImage.user_id == user_id).all()
    
    @staticmethod
    def get_all_face_images(db: Session) -> List[models.FaceImage]:
        """Get all face images in the database (sync version for backward compatibility)."""
        return db.query(models.FaceImage).all()
    
    @staticmethod
    def verify_face(db: Session, verification_data: FaceVerification) -> Dict[str, Any]:
        """Verify a face against stored embeddings (sync version for backward compatibility)."""
        # Decode the image and extract embedding
        image_array = FaceService._decode_base64_image(verification_data.image_data)
        new_embedding = FaceService._extract_face_embedding(image_array)
        
        if not new_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the verification image"
            )
        
        # Convert to numpy array for comparison
        new_embedding_array = np.array(new_embedding)
        
        # Get user to verify against (if specified)
        if verification_data.user_id:
            # Get face images for specific user
            face_images = FaceService.get_user_face_images(db, verification_data.user_id)
            if not face_images:
                return {
                    "verified": False,
                    "message": "No reference faces found for this user"
                }
        else:
            # Get all face images (for identification)
            face_images = FaceService.get_all_face_images(db)
            if not face_images:
                return {
                    "verified": False,
                    "message": "No reference faces found in the system"
                }
        
        # Find best match
        best_match = FaceService._find_best_match(new_embedding_array, face_images)
        
        if best_match:
            user_id, similarity = best_match
            
            # Get user details
            user = db.query(models.User).filter(models.User.id == user_id).first()
            
            return {
                "verified": True,
                "user_id": user_id,
                "similarity": similarity,
                "username": user.username if user else None,
                "full_name": user.full_name if user else None
            }
        
        return {
            "verified": False,
            "message": "No matching face found"
        }
    
    @staticmethod
    def delete_face_image(db: Session, face_id: int) -> bool:
        """Delete a face image by ID (sync version for backward compatibility)."""
        face_image = db.query(models.FaceImage).filter(models.FaceImage.id == face_id).first()
        
        if not face_image:
            return False
            
        db.delete(face_image)
        db.commit()
        
        return True
