"""
Programmatically run Alembic migrations from Python code (e.g., FastAPI startup).
"""
import os
from alembic.config import Config
from alembic import command

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
import sqlalchemy as sa
import os

from app.core.settings import settings

def run_alembic_upgrade():
    # Path to alembic.ini (assume project structure: backend/alembic.ini)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_ini_path = os.path.join(base_dir, 'alembic.ini')
    alembic_dir = os.path.join(base_dir, 'alembic')

    # Patch for Alembic: always use sync driver
    alembic_db_url = settings.DATABASE_URL
    if "+asyncpg" in alembic_db_url:
        alembic_db_url = alembic_db_url.replace("+asyncpg", "")
    if "+aiosqlite" in alembic_db_url:
        alembic_db_url = alembic_db_url.replace("+aiosqlite", "")

    config = Config(alembic_ini_path)
    config.set_main_option('script_location', alembic_dir)
    config.set_main_option('sqlalchemy.url', alembic_db_url)

    # Get head revision
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()

    # Get current revision from DB
    engine = sa.create_engine(alembic_db_url)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT version_num FROM alembic_version"))
        row = result.first()
        current_revision = row[0] if row else None

    if current_revision == head_revision:
        print("Database is already up to date. No migrations to apply.")
        return

    command.upgrade(config, 'head')
