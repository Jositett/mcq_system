import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM tests")
        await session.commit()

async def get_instructor_token(async_client: AsyncClient):
    user_data = {
        "username": "instructor2",
        "email": "instructor2@example.com",
        "full_name": "Instructor Two",
        "role": "instructor",
        "password": "instructorpass2"
    }
    await async_client.post("/api/auth/register", json=user_data)
    login_data = {"username": "instructor2", "password": "instructorpass2"}
    response = await async_client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_instructor_can_list_tests(async_client: AsyncClient):
    token = await get_instructor_token(async_client)
    response = await async_client.get("/api/tests/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
