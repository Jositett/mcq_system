import base64
from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_student_token():
    # Register the user if not present
    reg_payload = {
        "username": "student1",
        "email": "student1@example.com",
        "full_name": "Student One",
        "password": "password",
        "role": "student"
    }
    client.post("/api/auth/register", json=reg_payload)
    response = client.post("/api/auth/login", json={"username": "student1", "password": "password"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]

def test_upload_face_image_valid():
    token = get_student_token()
    # Use a real face image base64 for best results; here we use a 1x1 PNG (no face, will fail embedding)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400  # Should fail: no face detected
    

def test_upload_face_image_no_face():
    token = get_student_token()
    # Use a blank image (no face)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "No face detected" in response.text

import os

def load_image_base64(filename):
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def test_upload_with_embedding_only():
    token = get_student_token()
    # Simulate JS embedding
    embedding = ','.join([str(0.01 * i) for i in range(128)])
    payload = {
        "embedding": embedding,
        "image_data": "irrelevant",
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["embedding"] == embedding

def test_upload_with_image_only():
    token = get_student_token()
    img_base64 = load_image_base64("face1.jpg")
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user_id"] > 0
    assert data["embedding"] and len(data["embedding"]) > 0

def test_upload_with_both_embedding_and_image():
    token = get_student_token()
    embedding = ','.join([str(0.02 * i) for i in range(128)])
    img_base64 = load_image_base64("face1.jpg")
    payload = {
        "embedding": embedding,
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["embedding"] == embedding

def test_upload_with_invalid_embedding():
    token = get_student_token()
    payload = {
        "embedding": "not_a_valid_embedding",
        "image_data": "irrelevant",
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Invalid embedding format" in response.text

def test_upload_real_face_image_no_face():
    token = get_student_token()
    img_base64 = load_image_base64("blank.jpg")  # Provide a blank image for this test
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "No face detected" in response.text

def test_get_my_face_images():
    token = get_student_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/face/my-images", headers=headers)
    assert response.status_code == 200
    images = response.json()
    assert isinstance(images, list)
    if images:
        assert "image_data" in images[0]
        assert "user_id" in images[0]
