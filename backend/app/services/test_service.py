from sqlalchemy.orm import Session
from app.db import models
from app.schemas.test import TestCreate
from app.schemas.bulk_question import BulkQuestionUploadItem, BulkQuestionUploadResponseItem
import json

def create_test(db: Session, test: TestCreate):
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

def list_tests(db: Session):
    return db.query(models.Test).all()

def bulk_question_upload(db: Session, questions: list[BulkQuestionUploadItem], instructor_id: int = None) -> list[BulkQuestionUploadResponseItem]:
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
