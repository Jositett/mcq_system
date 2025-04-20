from sqlalchemy.orm import Session
from app.db import models

def get_student_tests(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return []
    batch_id = student.batch_id
    return db.query(models.Test).filter(models.Test.batch_id == batch_id).all()

def get_student_attendance(db: Session, student_id: int):
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
