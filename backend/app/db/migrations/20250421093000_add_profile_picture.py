"""
Migration: add_profile_picture
Version: 20250421093000
"""

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def upgrade_async(session: AsyncSession) -> None:
    """Add profile_picture column to users table if it doesn't exist."""
    await session.execute(text(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name = 'profile_picture'
            ) THEN
                ALTER TABLE users
                ADD COLUMN profile_picture TEXT;
            END IF;
        END$$;
        """
    ))


def upgrade(session: Session) -> None:
    """Sync: Add profile_picture column to users table if it doesn't exist."""
    session.execute(text(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name = 'profile_picture'
            ) THEN
                ALTER TABLE users
                ADD COLUMN profile_picture TEXT;
            END IF;
        END$$;
        """
    ))


async def downgrade_async(session: AsyncSession) -> None:
    """Remove profile_picture column from users table if it exists."""
    await session.execute(text(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name = 'profile_picture'
            ) THEN
                ALTER TABLE users
                DROP COLUMN profile_picture;
            END IF;
        END$$;
        """
    ))


def downgrade(session: Session) -> None:
    """Sync: Remove profile_picture column from users table if it exists."""
    session.execute(text(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name = 'profile_picture'
            ) THEN
                ALTER TABLE users
                DROP COLUMN profile_picture;
            END IF;
        END$$;
        """
    ))
