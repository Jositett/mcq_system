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

def get_instructor_token():
    user_data = {
        "username": "instructor2",
        "email": "instructor2@example.com",
        "full_name": "Instructor Two",
        "role": "instructor",
        "password": "instructorpass2"
    }
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "instructor2", "password": "instructorpass2"}
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]

def test_instructor_can_list_tests():
    token = get_instructor_token()
    response = client.get("/api/tests/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
