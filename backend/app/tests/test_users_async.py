import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    user_data = {
        "username": "asyncuser",
        "email": "asyncuser@example.com",
        "full_name": "Async User",
        "role": "student",
        "password": "asyncpass"
    }
    resp = await async_client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    login_data = {"username": "asyncuser", "password": "asyncpass"}
    login = await async_client.post("/api/auth/login", json=login_data)
    assert login.status_code == 200
    assert "access_token" in login.json()
