import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, SessionLocal
from app.db import models

# Ensure test DB tables are created
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users_table():
    db = SessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_and_login():
    # Register
    user_data = {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "full_name": "Test Admin",
        "role": "admin",
        "password": "testpass123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    # Login
    login_data = {"username": "testadmin", "password": "testpass123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
