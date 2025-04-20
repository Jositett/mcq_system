from sqlalchemy.orm import Session
from app.db import models
from app.schemas.test import TestCreate
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
