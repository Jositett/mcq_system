import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, SessionLocal
from app.db import models

models.Base.metadata.create_all(bind=engine)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users_table():
    db = SessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()

def get_admin_token():
    # Register admin if not exists
    user_data = {
        "username": "adminuser",
        "email": "adminuser@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "password": "adminpass"
    }
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "adminuser", "password": "adminpass"}
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

def test_admin_can_list_users():
    token = get_admin_token()
    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_can_create_and_delete_user():
    token = get_admin_token()
    # Create user
    user_data = {
        "username": "studentuser",
        "email": "studentuser@example.com",
        "full_name": "Student User",
        "role": "student",
        "password": "studentpass"
    }
    client.post("/api/auth/register", json=user_data)
    # Get user list and find new user id
    users = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"}).json()
    user = next((u for u in users if u["username"] == "studentuser"), None)
    assert user is not None
    # Delete user
    response = client.delete(f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"
