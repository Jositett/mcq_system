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

@pytest.fixture(autouse=True)
def clear_attendance_table():
    db = SessionLocal()
    db.query(models.Attendance).delete()
    db.commit()
    db.close()

def get_student_token():
    user_data = {
        "username": "student2",
        "email": "student2@example.com",
        "full_name": "Student Two",
        "role": "student",
        "password": "studentpass2"
    }
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "student2", "password": "studentpass2"}
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"], response.json()

import datetime

def test_face_checkin_flow():
    token, login_resp = get_student_token()
    student_id = login_resp.get("user_id") or 1
    # Use a blank image (no face)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(datetime.date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    # Upload face (will fail, no face detected)
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    # Try face check-in (should fail, no registered face)
    checkin_payload = {"image": img_base64}
    checkin = client.post("/api/attendance/face-checkin", json=checkin_payload, headers=headers)
    assert checkin.status_code == 400
    # For a real test, use a real face image for both upload and check-in, and assert success

def test_checkin_with_embedding_only():
    token, _ = get_student_token()
    # Register embedding
    embedding = ','.join([str(0.03 * i) for i in range(128)])
    payload = {
        "embedding": embedding,
        "image_data": "irrelevant",
        "created_at": str(datetime.date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    reg = client.post("/api/face/upload", json=payload, headers=headers)
    assert reg.status_code == 200, reg.text
    # Check-in with the same embedding
    checkin_payload = {"embedding": embedding}
    checkin = client.post("/api/attendance/face-checkin", json=checkin_payload, headers=headers)
    assert checkin.status_code == 200, checkin.text

def test_checkin_with_image_only():
    token, _ = get_student_token()
    from app.tests.test_face import load_image_base64
    img1_base64 = load_image_base64("face1.jpg")
    payload = {
        "image_data": img1_base64,
        "created_at": str(datetime.date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    reg = client.post("/api/face/upload", json=payload, headers=headers)
    assert reg.status_code == 200, reg.text
    checkin_payload = {"image": img1_base64}
    checkin = client.post("/api/attendance/face-checkin", json=checkin_payload, headers=headers)
    assert checkin.status_code == 200, checkin.text

def test_checkin_with_both_embedding_and_image():
    token, _ = get_student_token()
    embedding = ','.join([str(0.04 * i) for i in range(128)])
    from app.tests.test_face import load_image_base64
    img1_base64 = load_image_base64("face1.jpg")
    payload = {
        "embedding": embedding,
        "image_data": img1_base64,
        "created_at": str(datetime.date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    reg = client.post("/api/face/upload", json=payload, headers=headers)
    assert reg.status_code == 200, reg.text
    checkin_payload = {"embedding": embedding, "image": img1_base64}
    checkin = client.post("/api/attendance/face-checkin", json=checkin_payload, headers=headers)
    assert checkin.status_code == 200, checkin.text

def test_checkin_with_invalid_embedding():
    token, _ = get_student_token()
    payload = {
        "embedding": "not_a_valid_embedding"
    }
    headers = {"Authorization": f"Bearer {token}"}
    checkin = client.post("/api/attendance/face-checkin", json=payload, headers=headers)
    assert checkin.status_code == 400
    assert "Invalid embedding format" in checkin.text
