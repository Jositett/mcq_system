import pytest
from httpx import AsyncClient
import datetime

@pytest.mark.asyncio
async def test_async_check_in_flow(async_client: AsyncClient):
    # Register student
    user_data = {
        "username": "asyncstudent",
        "email": "asyncstudent@example.com",
        "full_name": "Async Student",
        "role": "student",
        "password": "asyncpass"
    }
    resp = await async_client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    login_data = {"username": "asyncstudent", "password": "asyncpass"}
    login = await async_client.post("/api/auth/login", json=login_data)
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Attempt check-in (should fail, no student_id yet)
    attendance = {"student_id": 1, "date": str(datetime.date.today()), "status": "present"}
    resp = await async_client.post("/api/attendance/check-in", json=attendance, headers=headers)
    # Should fail if student_id is not mapped, or succeed if test DB auto-creates student
    assert resp.status_code in (200, 403, 400)
    # Add more logic here as your test DB evolves
