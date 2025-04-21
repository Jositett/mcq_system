"""
Database initialization module.
This module provides functions to initialize the database and run migrations.
"""

import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.migrations_core import run_migrations, run_migrations_async
from app.core.settings import settings
from app.db.session import get_db, get_async_db

logger = logging.getLogger(__name__)


async def init_db_async() -> None:
    """Initialize the database with async SQLAlchemy."""
    try:
        logger.info("Initializing database (async)...")
        
        # Run migrations
        await run_migrations_async()
        
        logger.info("Database initialization completed (async)")
    except Exception as e:
        logger.error(f"Error initializing database (async): {str(e)}")
        raise


def init_db() -> None:
    """Initialize the database with sync SQLAlchemy."""
    try:
        logger.info("Initializing database...")
        
        # Run migrations
        run_migrations()
        
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


if __name__ == "__main__":
    # When run as a script, initialize the database
    logging.basicConfig(level=logging.INFO)
    
    if settings.ENV == "test":
        logger.warning("Initializing database in test environment")
    
    # Use async version if possible
    try:
        asyncio.run(init_db_async())
    except Exception:
        logger.warning("Async database initialization failed, falling back to sync")
        init_db()
