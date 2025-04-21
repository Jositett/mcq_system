import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM students")
        await session.commit()

async def get_student_token(async_client: AsyncClient):
    user_data = {
        "username": "student1",
        "email": "student1@example.com",
        "full_name": "Student One",
        "role": "student",
        "password": "studentpass1"
    }
    await async_client.post("/api/auth/register", json=user_data)
    login_data = {"username": "student1", "password": "studentpass1"}
    response = await async_client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_student_cannot_list_users(async_client: AsyncClient):
    token = await get_student_token(async_client)
    response = await async_client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 or response.status_code == 401

@pytest.mark.asyncio
async def test_student_can_login_and_get_token(async_client: AsyncClient):
    token = await get_student_token(async_client)
    assert isinstance(token, str)
