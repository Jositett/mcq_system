from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core import security
from app.db.session import get_db
from app.db import models
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

from app.services import user_service

@router.post(
    '/register',
    response_model=UserResponse,
    tags=["Auth"],
    summary="Register a new user",
    description="Registers a new user (admin, instructor, or student).",
    responses={
        200: {"description": "User registered successfully."},
        400: {"description": "Username or email already registered."}
    },
    response_description="Registered user info."
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = user_service.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    return db_user

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post(
    '/login',
    tags=["Auth"],
    summary="Login and get JWT token",
    description="Authenticate with username and password to receive a JWT token.",
    responses={
        200: {"description": "Login successful, JWT token and user info returned."},
        401: {"description": "Invalid credentials."}
    },
    response_description="JWT access token and user info."
)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT token and user info."""
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = security.create_access_token({"sub": user.username, "role": user.role})
    # Return both token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role
        }
    }
