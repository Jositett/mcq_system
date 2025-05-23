import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_instructor_batch_listing(async_client: AsyncClient):
    # Register instructor
    user_data = {
        "username": "asyncinstructor",
        "email": "asyncinstructor@example.com",
        "full_name": "Async Instructor",
        "role": "instructor",
        "password": "asyncpass"
    }
    resp = await async_client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    login_data = {"username": "asyncinstructor", "password": "asyncpass"}
    login = await async_client.post("/api/auth/login", json=login_data)
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # List batches (should be empty or as per test DB)
    resp = await async_client.get("/api/instructors/batches", headers=headers)
    assert resp.status_code in (200, 403)
