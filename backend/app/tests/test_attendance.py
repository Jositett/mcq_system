import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
async def clear_users_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM users")
        await session.commit()

@pytest.fixture(autouse=True)
async def clear_attendance_table():
    async with AsyncSessionLocal() as session:
        await session.execute("DELETE FROM attendance")
        await session.commit()

async def get_student_token(async_client: AsyncClient):
    user_data = {
        "username": "student2",
        "email": "student2@example.com",
        "full_name": "Student Two",
        "role": "student",
        "password": "studentpass2"
    }
    await async_client.post("/api/auth/register", json=user_data)
    login_data = {"username": "student2", "password": "studentpass2"}
    response = await async_client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"], response.json()

import datetime

@pytest.mark.asyncio
async def test_face_checkin_flow(async_client: AsyncClient):
    token, login_resp = await get_student_token(async_client)
    student_id = login_resp.get("user_id") or 1
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(datetime.date.today())
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=headers)
    assert response.status_code == 400
    checkin_payload = {"image": img_base64}
    checkin = await async_client.post("/api/attendance/face-checkin", json=checkin_payload, headers=headers)
    assert checkin.status_code == 400

@pytest.mark.asyncio
async def test_checkin_with_image_only(async_client: AsyncClient):
    token, _ = await get_student_token(async_client)
    img_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/6X6kXwAAAAASUVORK5CYII="
    payload = {
        "image_data": img_base64,
        "created_at": str(datetime.date.today())
    }
    token_header = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=token_header)
    assert response.status_code == 400
    checkin_payload = {"image": img_base64}
    checkin = await async_client.post("/api/attendance/face-checkin", json=checkin_payload, headers=token_header)
    assert checkin.status_code == 400

@pytest.mark.asyncio
async def test_checkin_with_embedding_only(async_client: AsyncClient):
    token, _ = await get_student_token(async_client)
    embedding = ','.join([str(0.03 * i) for i in range(128)])
    payload = {
        "embedding": embedding,
        "image_data": "irrelevant",
        "created_at": str(datetime.date.today())
    }
    token_header = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=token_header)
    assert response.status_code == 200
    # Check-in with the same embedding
    checkin_payload = {"embedding": embedding}
    checkin = await async_client.post("/api/attendance/face-checkin", json=checkin_payload, headers=token_header)
    assert checkin.status_code == 200

@pytest.mark.asyncio
async def test_checkin_with_invalid_embedding(async_client: AsyncClient):
    token, _ = await get_student_token(async_client)
    embedding = 'not_a_valid_embedding'
    payload = {
        "embedding": embedding,
        "image_data": "irrelevant",
        "created_at": str(datetime.date.today())
    }
    token_header = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/face/upload", json=payload, headers=token_header)
    assert response.status_code == 400
    # Check-in with the same embedding
    checkin_payload = {"embedding": embedding}
    checkin = await async_client.post("/api/attendance/face-checkin", json=checkin_payload, headers=token_header)
    payload = {
        "embedding": "not_a_valid_embedding"
    }
    headers = {"Authorization": f"Bearer {token}"}
    checkin = client.post("/api/attendance/face-checkin", json=payload, headers=headers)
    assert checkin.status_code == 400
    assert "Invalid embedding format" in checkin.text
