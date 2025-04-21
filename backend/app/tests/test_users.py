import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM users")
        await session.commit()

async def get_admin_token(async_client: AsyncClient):
    user_data = {
        "username": "adminuser",
        "email": "adminuser@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "password": "adminpass"
    }
    await async_client.post("/api/auth/register", json=user_data)
    login_data = {"username": "adminuser", "password": "adminpass"}
    response = await async_client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_admin_can_list_users(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    response = await async_client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_admin_can_create_and_delete_user(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    user_data = {
        "username": "studentuser",
        "email": "studentuser@example.com",
        "full_name": "Student User",
        "role": "student",
        "password": "studentpass"
    }
    await async_client.post("/api/auth/register", json=user_data)
    users = (await async_client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})).json()
    user = next((u for u in users if u["username"] == "studentuser"), None)
    assert user is not None
    response = await async_client.delete(f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"
