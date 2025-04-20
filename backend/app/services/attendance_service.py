from sqlalchemy.orm import Session
from app.db import models
from app.schemas.attendance import AttendanceCreate
from datetime import date

def check_in(db: Session, attendance: AttendanceCreate):
    # Prevent duplicate check-in for the same date
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == attendance.student_id,
        models.Attendance.date == attendance.date
    ).first()
    if existing:
        return None
    db_attendance = models.Attendance(
        student_id=attendance.student_id,
        date=attendance.date,
        status=attendance.status
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def attendance_history(db: Session, student_id: int):
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
