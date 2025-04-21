from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db import models
from app.schemas.test import TestCreate
from app.schemas.bulk_question import BulkQuestionUploadItem, BulkQuestionUploadResponseItem
from typing import List, Optional, Dict, Any
from app.core.cache import async_cached
import json

# Async methods (modern approach)
async def create_test_async(db: AsyncSession, test: TestCreate) -> models.Test:
    """Create a new test with questions using async SQLAlchemy."""
    # Create test
    db_test = models.Test(
        name=test.name,
        batch_id=test.batch_id,
        scheduled_at=test.scheduled_at,
    )
    db.add(db_test)
    await db.commit()
    await db.refresh(db_test)
    
    # Add questions
    for q in test.questions:
        db_question = models.Question(
            test_id=db_test.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=json.dumps(q.options) if q.options else None,
            correct_answer=q.correct_answer,
        )
        db.add(db_question)
    
    await db.commit()
    await db.refresh(db_test)
    return db_test

@async_cached(ttl=60, key_prefix="tests_list")
async def list_tests_async(db: AsyncSession) -> List[models.Test]:
    """List all tests using async SQLAlchemy."""
    result = await db.execute(select(models.Test))
    return result.scalars().all()

async def get_test_async(db: AsyncSession, test_id: int) -> Optional[models.Test]:
    """Get a test by ID using async SQLAlchemy."""
    result = await db.execute(
        select(models.Test).where(models.Test.id == test_id)
    )
    return result.scalars().first()

async def get_test_questions_async(db: AsyncSession, test_id: int) -> List[models.Question]:
    """Get all questions for a test using async SQLAlchemy."""
    result = await db.execute(
        select(models.Question).where(models.Question.test_id == test_id)
    )
    return result.scalars().all()

async def bulk_question_upload_async(db: AsyncSession, questions: List[BulkQuestionUploadItem], instructor_id: Optional[int] = None) -> List[BulkQuestionUploadResponseItem]:
    """Bulk upload questions using async SQLAlchemy."""
    results = []
    
    for item in questions:
        try:
            # Find test (by name, restrict to instructor's batches if instructor_id is set)
            test_query = select(models.Test).where(models.Test.name == item.test_name)
            
            if instructor_id:
                test_query = select(models.Test).join(models.Batch).where(
                    (models.Test.name == item.test_name) & 
                    (models.Batch.instructor_id == instructor_id)
                )
            
            result = await db.execute(test_query)
            test = result.scalars().first()
            
            if not test:
                raise ValueError('Test not found. Please create the test first.')
            
            # Insert question
            db_question = models.Question(
                test_id=test.id,
                question_text=item.question_text,
                question_type=item.question_type,
                options=item.options,
                correct_answer=item.correct_answer
            )
            db.add(db_question)
            await db.commit()
            await db.refresh(db_question)
            
            results.append(BulkQuestionUploadResponseItem(
                question_text=item.question_text,
                test_name=item.test_name,
                success=True,
                error=None
            ))
        except Exception as e:
            await db.rollback()
            results.append(BulkQuestionUploadResponseItem(
                question_text=item.question_text,
                test_name=item.test_name,
                success=False,
                error=str(e)
            ))
    
    return results

# Sync methods (for backward compatibility)
def create_test(db: Session, test: TestCreate) -> models.Test:
    """Create a new test with questions (sync version for backward compatibility)."""
    db_test = models.Test(
        name=test.name,
        batch_id=test.batch_id,
        scheduled_at=test.scheduled_at,
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    # Add questions
    for q in test.questions:
        db_question = models.Question(
            test_id=db_test.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=json.dumps(q.options) if q.options else None,
            correct_answer=q.correct_answer,
        )
        db.add(db_question)
    db.commit()
    db.refresh(db_test)
    return db_test

def list_tests(db: Session) -> List[models.Test]:
    """List all tests (sync version for backward compatibility)."""
    return db.query(models.Test).all()

def bulk_question_upload(db: Session, questions: List[BulkQuestionUploadItem], instructor_id: Optional[int] = None) -> List[BulkQuestionUploadResponseItem]:
    """Bulk upload questions (sync version for backward compatibility)."""
    results = []
    for item in questions:
        try:
            # Find test (by name, restrict to instructor's batches if instructor_id is set)
            test_query = db.query(models.Test).filter(models.Test.name == item.test_name)
            if instructor_id:
                test_query = test_query.join(models.Batch).filter(models.Batch.instructor_id == instructor_id)
            test = test_query.first()
            if not test:
                raise ValueError('Test not found. Please create the test first.')
            # Insert question
            db_question = models.Question(
                test_id=test.id,
                question_text=item.question_text,
                question_type=item.question_type,
                options=item.options,
                correct_answer=item.correct_answer
            )
            db.add(db_question)
            db.commit()
            db.refresh(db_question)
            results.append(BulkQuestionUploadResponseItem(
                question_text=item.question_text,
                test_name=item.test_name,
                success=True,
                error=None
            ))
        except Exception as e:
            db.rollback()
            results.append(BulkQuestionUploadResponseItem(
                question_text=item.question_text,
                test_name=item.test_name,
                success=False,
                error=str(e)
            ))
    return results

def get_test(db: Session, test_id: int) -> Optional[models.Test]:
    """Get a test by ID (sync version for backward compatibility)."""
    return db.query(models.Test).filter(models.Test.id == test_id).first()

def get_test_questions(db: Session, test_id: int) -> List[models.Question]:
    """Get all questions for a test (sync version for backward compatibility)."""
    return db.query(models.Question).filter(models.Question.test_id == test_id).all()
