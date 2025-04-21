import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM users")
        await session.commit()

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    user_data = {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "full_name": "Test Admin",
        "role": "admin",
        "password": "testpass123"
    }
    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    login_data = {"username": "testadmin", "password": "testpass123"}
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
