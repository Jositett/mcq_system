from sqlalchemy.orm import Session
from app.db import models
from app.schemas.bulk_student import BulkStudentUploadItem, BulkStudentUploadResponseItem
from app.core import security
from sqlalchemy.exc import IntegrityError
from datetime import date

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

def get_student_tests(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return []
    batch_id = student.batch_id
    return db.query(models.Test).filter(models.Test.batch_id == batch_id).all()

def get_student_attendance(db: Session, student_id: int):
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
