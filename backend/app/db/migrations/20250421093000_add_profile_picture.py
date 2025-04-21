"""
Migration to add profile_picture column to users table.
"""

from app.db.migrations import MigrationScript


class Migration(MigrationScript):
    """Add profile_picture column to users table."""
    
    version = "20250421093000"
    description = "Add profile_picture column to users table"
    
    async def up(self):
        """Apply the migration."""
        await self.execute("""
        -- Add profile_picture column to users table if it doesn't exist
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
        END $$;
        """)
    
    async def down(self):
        """Revert the migration."""
        await self.execute("""
        -- Remove profile_picture column from users table if it exists
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
        END $$;
        """)
