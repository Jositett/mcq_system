import base64
from datetime import date
import pytest
from httpx import AsyncClient
from app.main import app

async def get_student_token(async_client: AsyncClient):
    reg_payload = {
        "username": "student1",
        "email": "student1@example.com",
        "full_name": "Student One",
        "password": "password",
        "role": "student"
    }
    await async_client.post("/api/auth/register", json=reg_payload)
    response = await async_client.post("/api/auth/login", json={"username": "student1", "password": "password"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_upload_face_image_valid(async_client: AsyncClient):
    token = await get_student_token(async_client)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400  # Should fail: no face detected

@pytest.mark.asyncio
async def test_upload_face_image_no_face(async_client: AsyncClient):
    token = await get_student_token(async_client)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "No face detected" in response.text

import os

async def load_image_base64(async_client: AsyncClient, filename):
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

@pytest.mark.asyncio
async def test_upload_with_embedding_only(async_client: AsyncClient):
    token = await get_student_token(async_client)
    embedding = ','.join([str(0.01 * i) for i in range(128)])
    payload = {
        "embedding": embedding,
        "image_data": "irrelevant",
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["embedding"] == embedding

@pytest.mark.asyncio
async def test_upload_with_image_only(async_client: AsyncClient):
    token = await get_student_token(async_client)
    img_base64 = await load_image_base64(async_client, "face1.jpg")
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user_id"] > 0
    assert data["embedding"] and len(data["embedding"]) > 0

@pytest.mark.asyncio
async def test_upload_with_both_embedding_and_image(async_client: AsyncClient):
    token = await get_student_token(async_client)
    embedding = ','.join([str(0.02 * i) for i in range(128)])
    img_base64 = await load_image_base64(async_client, "face1.jpg")
    payload = {
        "embedding": embedding,
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["embedding"] == embedding

@pytest.mark.asyncio
async def test_upload_with_invalid_embedding(async_client: AsyncClient):
    token = await get_student_token(async_client)
    payload = {
        "embedding": "not_a_valid_embedding",
        "image_data": "irrelevant",
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Invalid embedding format" in response.text

@pytest.mark.asyncio
async def test_upload_real_face_image_no_face(async_client: AsyncClient):
    token = await get_student_token(async_client)
    img_base64 = await load_image_base64(async_client, "blank.jpg")  # Provide a blank image for this test
    payload = {
        "image_data": img_base64,
        "created_at": str(date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    assert "No face detected" in response.text

@pytest.mark.asyncio
async def test_get_my_face_images(async_client: AsyncClient):
    token = await get_student_token(async_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/face/my-images", headers=headers)
    assert response.status_code == 200
    images = response.json()
    assert isinstance(images, list)
    if images:
        assert "image_data" in images[0]
        assert "user_id" in images[0]
