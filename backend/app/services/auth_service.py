from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import timedelta
from typing import Optional, Dict, Any

from app.db import models
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.settings import settings


# Async methods (modern approach)
async def authenticate_user_async(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user with username and password using async SQLAlchemy.
    
    Args:
        db: Async database session
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        User object if authentication is successful, None otherwise
    """
    # Find user by username
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(password, user.hashed_password):
        return None
        
    # Check if user is active
    if not user.is_active:
        return None
        
    return user


async def create_user_async(db: AsyncSession, user_data: UserCreate) -> models.User:
    """
    Create a new user using async SQLAlchemy.
    
    Args:
        db: Async database session
        user_data: User data for creation
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    result = await db.execute(select(models.User).where(models.User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Check if email already exists
    result = await db.execute(select(models.User).where(models.User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user object
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=getattr(user_data, 'phone', None),
        department=getattr(user_data, 'department', None),
        bio=getattr(user_data, 'bio', None),
        gender=getattr(user_data, 'gender', None),
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    # Save to database
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


# This function doesn't need async as it doesn't interact with the database
def create_token_response(user: models.User, expires_delta: Optional[timedelta] = None) -> Dict[str, Any]:
    """
    Create a token response for a user.
    
    Args:
        user: User to create token for
        expires_delta: Optional custom token expiration
        
    Returns:
        Dictionary with token and user info
    """
    # Create access token
    token_data = {
        "sub": user.username,
        "role": user.role,
        "user_id": user.id
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=expires_delta
    )
    
    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }
    }


# Sync methods (for backward compatibility)
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user with username and password (sync version for backward compatibility).
    
    Args:
        db: Database session
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        User object if authentication is successful, None otherwise
    """
    # Find user by username
    user = db.query(models.User).filter(models.User.username == username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(password, user.hashed_password):
        return None
        
    # Check if user is active
    if not user.is_active:
        return None
        
    return user


def create_user(db: Session, user_data: UserCreate) -> models.User:
    """
    Create a new user (sync version for backward compatibility).
    
    Args:
        db: Database session
        user_data: User data for creation
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user object
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=getattr(user_data, 'phone', None),
        department=getattr(user_data, 'department', None),
        bio=getattr(user_data, 'bio', None),
        gender=getattr(user_data, 'gender', None),
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
