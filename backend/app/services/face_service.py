from sqlalchemy.orm import Session
from datetime import date
from app.db import models
from app.schemas.face import FaceImageCreate

class FaceService:
    @staticmethod
    def create_face_image(db: Session, user_id: int, face_data: FaceImageCreate):
        db_face = models.FaceImage(
            user_id=user_id,
            image_data=face_data.image_data,
            embedding=face_data.embedding,
            created_at=face_data.created_at
        )
        db.add(db_face)
        db.commit()
        db.refresh(db_face)
        return db_face

    @staticmethod
    def get_user_face_images(db: Session, user_id: int):
        return db.query(models.FaceImage).filter(models.FaceImage.user_id == user_id).all()

    @staticmethod
    def get_all_face_images(db: Session):
        return db.query(models.FaceImage).all()
