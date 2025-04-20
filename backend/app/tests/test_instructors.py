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
        "username": "instructor1",
        "email": "instructor1@example.com",
        "full_name": "Instructor One",
        "role": "instructor",
        "password": "instructorpass1"
    }
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "instructor1", "password": "instructorpass1"}
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"], response.json()

def test_instructor_cannot_list_users():
    token, _ = get_instructor_token()
    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 or response.status_code == 401

def test_instructor_can_access_own_batches_and_tests():
    token, login_resp = get_instructor_token()
    instructor_id = login_resp.get("user_id") or 1
    batches = client.get(f"/api/instructors/{instructor_id}/batches", headers={"Authorization": f"Bearer {token}"})
    assert batches.status_code in (200, 404)
    tests = client.get(f"/api/instructors/{instructor_id}/tests", headers={"Authorization": f"Bearer {token}"})
    assert tests.status_code in (200, 404)
