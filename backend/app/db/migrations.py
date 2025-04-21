"""
Database migration system for the MCQ Test & Attendance System.
This module provides functions to manage database schema migrations.
"""

import os
import logging
import importlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.sql import select, insert

from app.core.settings import settings
from app.db.session import sync_engine, async_engine, SessionLocal, AsyncSessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Migration table definition
metadata = MetaData()
migrations = Table(
    'migrations',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('version', String, unique=True, nullable=False),
    Column('name', String, nullable=False),
    Column('applied_at', DateTime, nullable=False),
)

# Directory where migration scripts are stored
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')


async def ensure_migrations_table_exists_async() -> None:
    """Ensure the migrations table exists in the database."""
    async with async_engine.begin() as conn:
        # Check if migrations table exists
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'migrations')"
        ))
        table_exists = result.scalar()
        
        if not table_exists:
            # Create migrations table
            await conn.execute(text('''
                CREATE TABLE migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP NOT NULL
                )
            '''))
            logger.info("Created migrations table")


def ensure_migrations_table_exists() -> None:
    """Ensure the migrations table exists in the database (sync version)."""
    with sync_engine.connect() as conn:
        # Check if migrations table exists
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'migrations')"
        ))
        table_exists = result.scalar()
        
        if not table_exists:
            # Create migrations table
            conn.execute(text('''
                CREATE TABLE migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP NOT NULL
                )
            '''))
            conn.commit()
            logger.info("Created migrations table")


async def get_applied_migrations_async() -> List[str]:
    """Get a list of applied migration versions."""
    await ensure_migrations_table_exists_async()
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(migrations.c.version).order_by(migrations.c.version))
        return [row[0] for row in result.fetchall()]


def get_applied_migrations() -> List[str]:
    """Get a list of applied migration versions (sync version)."""
    ensure_migrations_table_exists()
    
    with SessionLocal() as session:
        result = session.execute(select(migrations.c.version).order_by(migrations.c.version))
        return [row[0] for row in result.fetchall()]


def get_available_migrations() -> List[Dict[str, str]]:
    """Get a list of available migration scripts."""
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)
        return []
    
    migrations_list = []
    
    for filename in sorted(os.listdir(MIGRATIONS_DIR)):
        if filename.endswith('.py') and not filename.startswith('__'):
            version, name = filename[:-3].split('_', 1)
            migrations_list.append({
                'version': version,
                'name': name,
                'filename': filename
            })
    
    return migrations_list


async def apply_migration_async(migration: Dict[str, str], session: AsyncSession) -> None:
    """Apply a single migration."""
    version = migration['version']
    name = migration['name']
    filename = migration['filename']
    
    # Import the migration module
    module_path = f"app.db.migrations.{filename[:-3]}"
    migration_module = importlib.import_module(module_path)
    
    # Apply the migration
    logger.info(f"Applying migration {version}: {name}")
    
    if hasattr(migration_module, 'upgrade_async'):
        await migration_module.upgrade_async(session)
    elif hasattr(migration_module, 'upgrade'):
        # Fall back to sync version if async version is not available
        with SessionLocal() as sync_session:
            migration_module.upgrade(sync_session)
    else:
        raise ValueError(f"Migration {version} has no upgrade function")
    
    # Record the migration
    await session.execute(
        insert(migrations).values(
            version=version,
            name=name,
            applied_at=datetime.now()
        )
    )
    await session.commit()
    
    logger.info(f"Applied migration {version}: {name}")


def apply_migration(migration: Dict[str, str], session: Session) -> None:
    """Apply a single migration (sync version)."""
    version = migration['version']
    name = migration['name']
    filename = migration['filename']
    
    # Import the migration module
    module_path = f"app.db.migrations.{filename[:-3]}"
    migration_module = importlib.import_module(module_path)
    
    # Apply the migration
    logger.info(f"Applying migration {version}: {name}")
    
    if hasattr(migration_module, 'upgrade'):
        migration_module.upgrade(session)
    else:
        raise ValueError(f"Migration {version} has no upgrade function")
    
    # Record the migration
    session.execute(
        insert(migrations).values(
            version=version,
            name=name,
            applied_at=datetime.now()
        )
    )
    session.commit()
    
    logger.info(f"Applied migration {version}: {name}")


async def run_migrations_async() -> None:
    """Run all pending migrations."""
    # Ensure migrations directory exists
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)
    
    # Get applied and available migrations
    applied_migrations = await get_applied_migrations_async()
    available_migrations = get_available_migrations()
    
    # Filter out migrations that have already been applied
    pending_migrations = [m for m in available_migrations if m['version'] not in applied_migrations]
    
    if not pending_migrations:
        logger.info("No pending migrations to apply")
        return
    
    # Apply pending migrations
    logger.info(f"Applying {len(pending_migrations)} pending migrations")
    
    async with AsyncSessionLocal() as session:
        for migration in pending_migrations:
            await apply_migration_async(migration, session)
    
    logger.info("All migrations applied successfully")


def run_migrations() -> None:
    """Run all pending migrations (sync version)."""
    # Ensure migrations directory exists
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)
    
    # Get applied and available migrations
    applied_migrations = get_applied_migrations()
    available_migrations = get_available_migrations()
    
    # Filter out migrations that have already been applied
    pending_migrations = [m for m in available_migrations if m['version'] not in applied_migrations]
    
    if not pending_migrations:
        logger.info("No pending migrations to apply")
        return
    
    # Apply pending migrations
    logger.info(f"Applying {len(pending_migrations)} pending migrations")
    
    with SessionLocal() as session:
        for migration in pending_migrations:
            apply_migration(migration, session)
    
    logger.info("All migrations applied successfully")


def create_migration(name: str) -> str:
    """Create a new migration file."""
    # Ensure migrations directory exists
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)
    
    # Generate version based on timestamp
    version = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Sanitize name
    name = name.lower().replace(' ', '_').replace('-', '_')
    
    # Create filename
    filename = f"{version}_{name}.py"
    filepath = os.path.join(MIGRATIONS_DIR, filename)
    
    # Create migration file
    with open(filepath, 'w') as f:
        f.write('''"""
Migration: {name}
Version: {version}
"""

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def upgrade_async(session: AsyncSession) -> None:
    """Apply the migration using async SQLAlchemy."""
    # TODO: Implement migration logic
    await session.execute(text("""
        -- Add your SQL migration here
        -- Example:
        -- CREATE TABLE example (
        --     id SERIAL PRIMARY KEY,
        --     name VARCHAR(255) NOT NULL
        -- );
    """))


def upgrade(session: Session) -> None:
    """Apply the migration using sync SQLAlchemy."""
    # TODO: Implement migration logic
    session.execute(text("""
        -- Add your SQL migration here
        -- Example:
        -- CREATE TABLE example (
        --     id SERIAL PRIMARY KEY,
        --     name VARCHAR(255) NOT NULL
        -- );
    """))


async def downgrade_async(session: AsyncSession) -> None:
    """Revert the migration using async SQLAlchemy."""
    # TODO: Implement downgrade logic
    await session.execute(text("""
        -- Add your SQL downgrade here
        -- Example:
        -- DROP TABLE example;
    """))


def downgrade(session: Session) -> None:
    """Revert the migration using sync SQLAlchemy."""
    # TODO: Implement downgrade logic
    session.execute(text("""
        -- Add your SQL downgrade here
        -- Example:
        -- DROP TABLE example;
    """))
'''.format(name=name, version=version))
    
    logger.info(f"Created migration file: {filename}")
    return filepath


if __name__ == "__main__":
    # When run as a script, apply all pending migrations
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    if settings.ENV == "test":
        logger.warning("Running migrations in test environment")
    
    asyncio.run(run_migrations_async())
