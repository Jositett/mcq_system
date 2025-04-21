from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any

from app.db import models
from app.schemas.user import UserCreate, UserUpdate
from app.core import security


# Async methods (modern approach)
async def create_user_async(db: AsyncSession, user: UserCreate) -> Optional[models.User]:
    """Create a new user with async SQLAlchemy."""
    hashed_password = security.get_password_hash(user.password)
    
    # Check if username already exists
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    if result.scalars().first():
        return None
        
    # Check if email already exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalars().first():
        return None
    
    # Create new user
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        profile_picture=user.profile_picture,
    )
    
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        return None


async def authenticate_user_async(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
    """Authenticate a user with async SQLAlchemy."""
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    
    if not user:
        return None
        
    if not security.verify_password(password, user.hashed_password):
        return None
        
    return user


async def get_user_async(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get a user by ID with async SQLAlchemy."""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_username_async(db: AsyncSession, username: str) -> Optional[models.User]:
    """Get a user by username with async SQLAlchemy."""
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()


async def list_users_async(db: AsyncSession) -> List[models.User]:
    """List all users with async SQLAlchemy."""
    result = await db.execute(select(models.User))
    return result.scalars().all()


async def update_user_async(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[models.User]:
    """Update a user with async SQLAlchemy."""
    # Get user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = security.get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update user
    stmt = update(models.User).where(models.User.id == user_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    
    # Get updated user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def delete_user_async(db: AsyncSession, user_id: int) -> bool:
    """Delete a user with async SQLAlchemy."""
    # Check if user exists
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return False
    
    # Delete user
    await db.delete(user)
    await db.commit()
    
    return True


# Sync methods (for backward compatibility)
def create_user(db: Session, user: UserCreate) -> Optional[models.User]:
    """Create a new user (sync version for backward compatibility)."""
    hashed_password = security.get_password_hash(user.password)
    
    # Check if username or email already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        return None
        
    if db.query(models.User).filter(models.User.email == user.email).first():
        return None
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate a user (sync version for backward compatibility)."""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID (sync version for backward compatibility)."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def list_users(db: Session) -> List[models.User]:
    """List all users (sync version for backward compatibility)."""
    return db.query(models.User).all()


def update_user(db: Session, user_id: int, full_name: str = None, password: str = None) -> Optional[models.User]:
    """Update a user (sync version for backward compatibility)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    if full_name is not None:
        user.full_name = full_name
    if password is not None:
        user.hashed_password = security.get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user (sync version for backward compatibility)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
