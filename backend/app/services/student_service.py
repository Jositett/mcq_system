from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db import models
from app.schemas.bulk_student import BulkStudentUploadItem, BulkStudentUploadResponseItem
from app.core import security
from sqlalchemy.exc import IntegrityError
from datetime import date
from typing import List, Optional
from app.core.cache import async_cached

def bulk_student_upload(db: Session, students: list[BulkStudentUploadItem], instructor_id: int = None) -> list[BulkStudentUploadResponseItem]:
    results = []
    for item in students:
        try:
            # Find or create batch (instructor_id restricts batch for instructors)
            batch_query = db.query(models.Batch).filter(models.Batch.name == item.batch_name)
            if instructor_id:
                batch_query = batch_query.filter(models.Batch.instructor_id == instructor_id)
            batch = batch_query.first()
            if not batch:
                if instructor_id:
                    # Instructors can only create batches for themselves
                    batch = models.Batch(name=item.batch_name, instructor_id=instructor_id)
                else:
                    batch = models.Batch(name=item.batch_name)
                db.add(batch)
                db.commit()
                db.refresh(batch)
            # Check for existing user
            user = db.query(models.User).filter(models.User.email == item.email).first()
            if user:
                raise ValueError('User with this email already exists')
            # Create user
            password = security.generate_random_password() if hasattr(security, 'generate_random_password') else 'changeme123'
            user = models.User(
                username=item.email.split('@')[0],
                email=item.email,
                full_name=item.full_name,
                hashed_password=security.get_password_hash(password),
                role='student',
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            # Create student
            student = models.Student(
                user_id=user.id,
                batch_id=batch.id,
                roll_number=item.roll_number,
                dob=item.dob
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            results.append(BulkStudentUploadResponseItem(
                full_name=item.full_name,
                email=item.email,
                batch_name=item.batch_name,
                success=True,
                error=None
            ))
        except Exception as e:
            db.rollback()
            results.append(BulkStudentUploadResponseItem(
                full_name=item.full_name,
                email=item.email,
                batch_name=item.batch_name,
                success=False,
                error=str(e)
            ))
    return results

# Async methods (modern approach)
@async_cached(ttl=60, key_prefix="student_tests")
async def get_student_tests_async(db: AsyncSession, student_id: int) -> List[models.Test]:
    """Get all tests for a student with async SQLAlchemy."""
    # Get student
    result = await db.execute(
        select(models.Student).where(models.Student.id == student_id)
    )
    student = result.scalars().first()
    
    if not student:
        return []
    
    # Get tests for student's batch
    batch_id = student.batch_id
    result = await db.execute(
        select(models.Test).where(models.Test.batch_id == batch_id)
    )
    return result.scalars().all()

@async_cached(ttl=60, key_prefix="student_attendance")
async def get_student_attendance_async(db: AsyncSession, student_id: int) -> List[models.Attendance]:
    """Get attendance records for a student with async SQLAlchemy."""
    result = await db.execute(
        select(models.Attendance).where(models.Attendance.student_id == student_id)
    )
    return result.scalars().all()

async def bulk_student_upload_async(db: AsyncSession, students: List[BulkStudentUploadItem], instructor_id: Optional[int] = None) -> List[BulkStudentUploadResponseItem]:
    """Bulk upload students with async SQLAlchemy."""
    results = []
    
    for item in students:
        try:
            # Find or create batch (instructor_id restricts batch for instructors)
            result = await db.execute(
                select(models.Batch).where(models.Batch.name == item.batch_name)
            )
            if instructor_id:
                result = await db.execute(
                    select(models.Batch).where(
                        (models.Batch.name == item.batch_name) & 
                        (models.Batch.instructor_id == instructor_id)
                    )
                )
            
            batch = result.scalars().first()
            
            if not batch:
                if instructor_id:
                    # Instructors can only create batches for themselves
                    batch = models.Batch(name=item.batch_name, instructor_id=instructor_id)
                else:
                    batch = models.Batch(name=item.batch_name)
                db.add(batch)
                await db.commit()
                await db.refresh(batch)
            
            # Check for existing user
            result = await db.execute(
                select(models.User).where(models.User.email == item.email)
            )
            user = result.scalars().first()
            
            if user:
                raise ValueError('User with this email already exists')
            
            # Create user
            password = security.generate_random_password() if hasattr(security, 'generate_random_password') else 'changeme123'
            user = models.User(
                username=item.email.split('@')[0],
                email=item.email,
                full_name=item.full_name,
                hashed_password=security.get_password_hash(password),
                role='student',
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            # Create student
            student = models.Student(
                user_id=user.id,
                batch_id=batch.id,
                roll_number=item.roll_number,
                dob=item.dob
            )
            db.add(student)
            await db.commit()
            await db.refresh(student)
            
            results.append(BulkStudentUploadResponseItem(
                full_name=item.full_name,
                email=item.email,
                batch_name=item.batch_name,
                success=True,
                error=None
            ))
        except Exception as e:
            await db.rollback()
            results.append(BulkStudentUploadResponseItem(
                full_name=item.full_name,
                email=item.email,
                batch_name=item.batch_name,
                success=False,
                error=str(e)
            ))
    
    return results

# Sync methods (for backward compatibility)
def get_student_tests(db: Session, student_id: int) -> List[models.Test]:
    """Get all tests for a student (sync version for backward compatibility)."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return []
    batch_id = student.batch_id
    return db.query(models.Test).filter(models.Test.batch_id == batch_id).all()

def get_student_attendance(db: Session, student_id: int) -> List[models.Attendance]:
    """Get attendance records for a student (sync version for backward compatibility)."""
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
