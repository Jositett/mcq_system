from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db import models
from app.schemas.attendance import AttendanceCreate
from app.core.cache import async_cached
from typing import List, Optional, Dict, Any
from datetime import date

# Async methods (modern approach)
async def check_in_async(db: AsyncSession, attendance: AttendanceCreate) -> Optional[models.Attendance]:
    """Record attendance for a student using async SQLAlchemy."""
    # Prevent duplicate check-in for the same date
    result = await db.execute(
        select(models.Attendance).where(
            (models.Attendance.student_id == attendance.student_id) &
            (models.Attendance.date == attendance.date)
        )
    )
    existing = result.scalars().first()
    
    if existing:
        return None
        
    # Create new attendance record
    db_attendance = models.Attendance(
        student_id=attendance.student_id,
        date=attendance.date,
        status=attendance.status
    )
    
    db.add(db_attendance)
    await db.commit()
    await db.refresh(db_attendance)
    
    return db_attendance

@async_cached(ttl=60, key_prefix="attendance_history")
async def attendance_history_async(db: AsyncSession, student_id: int) -> List[models.Attendance]:
    """Get attendance history for a student using async SQLAlchemy."""
    result = await db.execute(
        select(models.Attendance).where(
            models.Attendance.student_id == student_id
        )
    )
    return result.scalars().all()

async def get_batch_attendance_async(db: AsyncSession, batch_id: int, date_value: Optional[date] = None) -> Dict[str, Any]:
    """Get attendance for all students in a batch for a specific date using async SQLAlchemy."""
    # Get all students in the batch
    result = await db.execute(
        select(models.Student).where(models.Student.batch_id == batch_id)
    )
    students = result.scalars().all()
    
    attendance_data = []
    for student in students:
        # Get user data for each student
        user_result = await db.execute(
            select(models.User).where(models.User.id == student.user_id)
        )
        user = user_result.scalars().first()
        
        # Get attendance for the specified date if provided
        attendance_query = select(models.Attendance).where(
            models.Attendance.student_id == student.id
        )
        
        if date_value:
            attendance_query = attendance_query.where(models.Attendance.date == date_value)
        
        attendance_result = await db.execute(attendance_query)
        attendances = attendance_result.scalars().all()
        
        # Add to result
        student_data = {
            "student_id": student.id,
            "user_id": user.id,
            "name": user.full_name,
            "roll_number": student.roll_number,
            "attendance": [
                {
                    "date": str(a.date),
                    "status": a.status
                } for a in attendances
            ]
        }
        attendance_data.append(student_data)
    
    return {
        "batch_id": batch_id,
        "date": str(date_value) if date_value else None,
        "students": attendance_data
    }

# Sync methods (for backward compatibility)
def check_in(db: Session, attendance: AttendanceCreate) -> Optional[models.Attendance]:
    """Record attendance for a student (sync version for backward compatibility)."""
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

def attendance_history(db: Session, student_id: int) -> List[models.Attendance]:
    """Get attendance history for a student (sync version for backward compatibility)."""
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()

def get_batch_attendance(db: Session, batch_id: int, date_value: Optional[date] = None) -> Dict[str, Any]:
    """Get attendance for all students in a batch for a specific date (sync version for backward compatibility)."""
    # Get all students in the batch
    students = db.query(models.Student).filter(models.Student.batch_id == batch_id).all()
    
    attendance_data = []
    for student in students:
        # Get user data for each student
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        
        # Get attendance for the specified date if provided
        attendance_query = db.query(models.Attendance).filter(
            models.Attendance.student_id == student.id
        )
        
        if date_value:
            attendance_query = attendance_query.filter(models.Attendance.date == date_value)
        
        attendances = attendance_query.all()
        
        # Add to result
        student_data = {
            "student_id": student.id,
            "user_id": user.id,
            "name": user.full_name,
            "roll_number": student.roll_number,
            "attendance": [
                {
                    "date": str(a.date),
                    "status": a.status
                } for a in attendances
            ]
        }
        attendance_data.append(student_data)
    
    return {
        "batch_id": batch_id,
        "date": str(date_value) if date_value else None,
        "students": attendance_data
    }
