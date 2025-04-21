from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db import models
from app.core.cache import async_cached

# Async methods (modern approach)
@async_cached(ttl=60, key_prefix="instructor_batches")
async def get_instructor_batches_async(db: AsyncSession, instructor_id: int) -> List[models.Batch]:
    """Get all batches for an instructor with async SQLAlchemy."""
    result = await db.execute(
        select(models.Batch).where(models.Batch.instructor_id == instructor_id)
    )
    return result.scalars().all()

@async_cached(ttl=60, key_prefix="instructor_tests")
async def get_instructor_tests_async(db: AsyncSession, instructor_id: int) -> List[models.Test]:
    """Get all tests for an instructor's batches with async SQLAlchemy."""
    # Get instructor's batches
    result = await db.execute(
        select(models.Batch).where(models.Batch.instructor_id == instructor_id)
    )
    batches = result.scalars().all()
    
    # Get batch IDs
    batch_ids = [batch.id for batch in batches]
    
    # If no batches, return empty list
    if not batch_ids:
        return []
    
    # Get tests for these batches
    result = await db.execute(
        select(models.Test).where(models.Test.batch_id.in_(batch_ids))
    )
    return result.scalars().all()

# Sync methods (for backward compatibility)
def get_instructor_batches(db: Session, instructor_id: int) -> List[models.Batch]:
    """Get all batches for an instructor (sync version for backward compatibility)."""
    return db.query(models.Batch).filter(models.Batch.instructor_id == instructor_id).all()

def get_instructor_tests(db: Session, instructor_id: int) -> List[models.Test]:
    """Get all tests for an instructor's batches (sync version for backward compatibility)."""
    batches = db.query(models.Batch).filter(models.Batch.instructor_id == instructor_id).all()
    batch_ids = [batch.id for batch in batches]
    
    # If no batches, return empty list
    if not batch_ids:
        return []
        
    return db.query(models.Test).filter(models.Test.batch_id.in_(batch_ids)).all()
