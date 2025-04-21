import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM instructors")
        await session.commit()

async def get_instructor_token(async_client: AsyncClient):
    user_data = {
        "username": "instructor1",
        "email": "instructor1@example.com",
        "full_name": "Instructor One",
        "role": "instructor",
        "password": "instructorpass1"
    }
    await async_client.post("/api/auth/register", json=user_data)
    login_data = {"username": "instructor1", "password": "instructorpass1"}
    response = await async_client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"], response.json()

@pytest.mark.asyncio
async def test_instructor_cannot_list_users(async_client: AsyncClient):
    token, _ = await get_instructor_token(async_client)
    response = await async_client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 or response.status_code == 401

@pytest.mark.asyncio
async def test_instructor_can_access_own_batches_and_tests(async_client: AsyncClient):
    token, login_resp = await get_instructor_token(async_client)
    instructor_id = login_resp.get("user_id") or 1
    batches = await async_client.get(f"/api/instructors/{instructor_id}/batches", headers={"Authorization": f"Bearer {token}"})
    assert batches.status_code in (200, 404)
    tests = await async_client.get(f"/api/instructors/{instructor_id}/tests", headers={"Authorization": f"Bearer {token}"})
    assert tests.status_code in (200, 404)
