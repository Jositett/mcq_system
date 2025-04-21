from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

# Create async engine based on the database URL
# Note: For SQLite, we need to modify the URL to use aiosqlite
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith('sqlite'):
    # Replace sqlite:// with sqlite+aiosqlite:// for async support
    DATABASE_URL = DATABASE_URL.replace('sqlite:', 'sqlite+aiosqlite:', 1)

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    # For SQLite only
    connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# For backward compatibility, also create a sync session
# This can be removed once all code is migrated to async
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if 'sqlite' in settings.DATABASE_URL else {}
)

SessionLocal = sync_sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Dependency for async database access
async def get_async_db():
    """Dependency that provides an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency for sync database access (for backward compatibility)
def get_db():
    """Dependency that provides a sync database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
