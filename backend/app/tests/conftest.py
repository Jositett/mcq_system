import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import models
from app.db.session import get_async_db
from app.db.migrations_core import run_migrations_async
import os
import builtins

DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Create async engine and session for testing
test_engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)
builtins.AsyncSessionLocal = TestingSessionLocal

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def run_migrations_before_tests():
    await run_migrations_async()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)

@pytest.fixture()
async def async_db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture()
async def async_client(async_db, setup_db):
    # Override dependency
    app.dependency_overrides[get_async_db] = lambda: async_db
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
