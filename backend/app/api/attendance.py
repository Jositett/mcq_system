from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
import face_recognition
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime

router = APIRouter()

from app.services import attendance_service, face_service
from app.schemas.attendance import AttendanceCreate
from app.core.dependencies import get_current_user, require_role
from app.db import models
from fastapi import Depends, Body
from pydantic import BaseModel

from typing import Optional
class FaceCheckinRequest(BaseModel):
    image: Optional[str] = None  # base64-encoded image
    embedding: Optional[str] = None  # embedding from client

class FaceCheckinResponse(BaseModel):
    success: bool
    message: str
    attendance_id: int | None = None

@router.post(
    '/check-in',
    tags=["Attendance"],
    summary="Check in with student ID and date",
    description="Standard check-in for a student using their ID, date, and status.",
    response_model=dict,
    responses={
        200: {"description": "Check-in successful."},
        400: {"description": "Already checked in for this date."},
        403: {"description": "Students can only check in for themselves."}
    },
    response_description="Check-in record."
)
def check_in(attendance: AttendanceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("student"))):
    """Check in for attendance using student ID and date."""
    if attendance.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Students can only check in for themselves.")
    db_attendance = attendance_service.check_in(db, attendance)
    if not db_attendance:
        raise HTTPException(status_code=400, detail="Already checked in for this date")
    return {
        "id": db_attendance.id,
        "student_id": db_attendance.student_id,
        "date": str(db_attendance.date),
        "status": db_attendance.status
    }

@router.post(
    '/face-checkin',
    tags=["Attendance", "Facial Recognition"],
    summary="Check in via facial recognition",
    description="Check in by submitting a base64-encoded face image. Used for training and check-in.",
    response_model=FaceCheckinResponse,
    responses={
        200: {"description": "Face check-in successful."},
        400: {"description": "Face not recognized or already checked in."},
        415: {"description": "Invalid image format."}
    },
    response_description="Result of face check-in."
)
def face_checkin(
    payload: FaceCheckinRequest = Body(..., examples={"default": {"summary": "Base64 image example", "value": {"image": "data:image/png;base64,iVBORw..."}}}),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("student"))
):
    """Check in by submitting a face image using facial recognition."""
    try:
        # Prefer embedding from client if provided
        if payload.embedding:
            try:
                import json
                emb = json.loads(payload.embedding) if payload.embedding.strip().startswith("[") else [float(x) for x in payload.embedding.split(",")]
                if not isinstance(emb, list) or len(emb) < 10:
                    raise ValueError
                face_encoding = np.array(emb)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid embedding format.")
        elif payload.image:
            # Fallback: extract embedding from image
            image_data = payload.image.split(',')[1] if ',' in payload.image else payload.image
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
        else:
            raise HTTPException(status_code=400, detail="No image or embedding provided.")
        
        # Get all stored face images for comparison
        stored_faces = face_service.FaceService.get_all_face_images(db)
        if not stored_faces:
            raise HTTPException(status_code=400, detail="No registered faces found in the system")
        
        # Compare with stored face encodings
        best_match = None
        min_distance = float('inf')
        
        for stored_face in stored_faces:
            # Convert stored embedding from string to numpy array
            stored_encoding = np.array([float(x) for x in stored_face.embedding.split(',')])
            distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            
            if distance < min_distance:
                min_distance = distance
                best_match = stored_face
        
        # Check if the best match is good enough (threshold = 0.6)
        if min_distance > 0.6:
            raise HTTPException(status_code=400, detail="Face not recognized")
        
        # Create attendance record
        attendance = AttendanceCreate(
            student_id=best_match.user_id,
            date=datetime.now().date(),
            status="present"
        )
        
        db_attendance = attendance_service.check_in(db, attendance)
        if not db_attendance:
            raise HTTPException(status_code=400, detail="Already checked in for today")
        
        return FaceCheckinResponse(
            success=True,
            message=f"Face check-in successful for student {best_match.user_id}",
            attendance_id=db_attendance.id
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


from typing import List

class AttendanceHistoryRecord(BaseModel):
    id: int
    date: str
    status: str

@router.get(
    '/history/{student_id}',
    tags=["Attendance"],
    summary="Get attendance history for a student",
    description="Returns a list of attendance records for the specified student.",
    response_model=List[AttendanceHistoryRecord],
    responses={
        200: {"description": "Attendance history returned."},
        403: {"description": "Students can only view their own attendance."}
    },
    response_description="List of attendance records."
)
def attendance_history(student_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("student"))):
    """Get attendance history for a student."""
    if student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Students can only view their own attendance.")
    records = attendance_service.attendance_history(db, student_id)
    return [
        {"id": r.id, "date": str(r.date), "status": r.status} for r in records
    ]

