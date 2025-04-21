import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_list_tests(async_client: AsyncClient):
    # Register instructor
    user_data = {
        "username": "testinstructor",
        "email": "testinstructor@example.com",
        "full_name": "Test Instructor",
        "role": "instructor",
        "password": "testpass"
    }
    resp = await async_client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    login_data = {"username": "testinstructor", "password": "testpass"}
    login = await async_client.post("/api/auth/login", json=login_data)
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # List tests (should be empty initially)
    resp = await async_client.get("/api/tests/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    # (You can expand this test to create a batch, then create a test, then list again)
