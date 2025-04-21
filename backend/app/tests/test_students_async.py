import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_student_registration_and_test_listing(async_client: AsyncClient):
    # Register student
    user_data = {
        "username": "teststudent",
        "email": "teststudent@example.com",
        "full_name": "Test Student",
        "role": "student",
        "password": "testpass"
    }
    resp = await async_client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    login_data = {"username": "teststudent", "password": "testpass"}
    login = await async_client.post("/api/auth/login", json=login_data)
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # List student tests (should be empty or as per test DB)
    resp = await async_client.get("/api/students/tests", headers=headers)
    assert resp.status_code in (200, 403)
    # (You can expand this test to enroll student in a batch, create a test, etc.)
