from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, get_async_db
from app.db import models
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service
from typing import Dict, Any
from datetime import timedelta
from app.core.settings import settings

# Create router with tags and prefix
router = APIRouter()

# Request and response models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user (admin, instructor, or student).",
    responses={
        201: {"description": "User registered successfully."},
        400: {"description": "Username or email already registered."}
    },
    response_description="Registered user info."
)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """Register a new user."""
    return await auth_service.create_user_async(db, user)

@router.post(
    '/login',
    response_model=Token,
    summary="Login and get JWT token",
    description="Authenticate with username and password to receive a JWT token.",
    responses={
        200: {"description": "Login successful, JWT token and user info returned."},
        401: {"description": "Invalid credentials."}
    },
    response_description="JWT access token and user info."
)
async def login(form_data: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """Login and get JWT token and user info."""
    # Authenticate user
    user = await auth_service.authenticate_user_async(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token response
    token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return auth_service.create_token_response(user, expires_delta=token_expires)

# For backward compatibility with sync clients
@router.post(
    '/register/sync',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (sync version)",
    description="Registers a new user (admin, instructor, or student) using synchronous API.",
    responses={
        201: {"description": "User registered successfully."},
        400: {"description": "Username or email already registered."}
    },
    response_description="Registered user info.",
    deprecated=True
)
def register_sync(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (sync version)."""
    return auth_service.create_user(db, user)

@router.post(
    '/login/sync',
    response_model=Token,
    summary="Login and get JWT token (sync version)",
    description="Authenticate with username and password to receive a JWT token using synchronous API.",
    responses={
        200: {"description": "Login successful, JWT token and user info returned."},
        401: {"description": "Invalid credentials."}
    },
    response_description="JWT access token and user info.",
    deprecated=True
)
def login_sync(form_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT token and user info (sync version)."""
    # Authenticate user
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token response
    token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return auth_service.create_token_response(user, expires_delta=token_expires)
