from sqlalchemy.orm import Session
from app.db import models

def get_instructor_batches(db: Session, instructor_id: int):
    return db.query(models.Batch).filter(models.Batch.instructor_id == instructor_id).all()

def get_instructor_tests(db: Session, instructor_id: int):
    batches = db.query(models.Batch).filter(models.Batch.instructor_id == instructor_id).all()
    batch_ids = [batch.id for batch in batches]
    return db.query(models.Test).filter(models.Test.batch_id.in_(batch_ids)).all()
