from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.settings import settings
from app.core.security import decode_access_token
# Use async DB session for user loading
from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import models
from jose import JWTError, jwt
from typing import Optional, List

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    """Validate JWT token and return current user, with detailed error feedback."""
    import logging
    logger = logging.getLogger("app.auth")
    
    # 1. Token missing
    if not token:
        logger.warning("No JWT token provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Invalid or expired JWT token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Extract username from token
    username: str = payload.get("sub")
    if username is None:
        logger.warning("JWT token missing subject (username). Payload: %s", payload)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing username (sub). Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. Get user from database
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    if user is None:
        logger.warning("User not found for username in token: %s", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def require_role(role: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
