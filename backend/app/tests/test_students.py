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

def get_student_token():
    # Register student if not exists
    user_data = {
        "username": "student1",
        "email": "student1@example.com",
        "full_name": "Student One",
        "role": "student",
        "password": "studentpass1"
    }
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "student1", "password": "studentpass1"}
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

def test_student_cannot_list_users():
    token = get_student_token()
    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 or response.status_code == 401

def test_student_can_login_and_get_token():
    token = get_student_token()
    assert isinstance(token, str)
