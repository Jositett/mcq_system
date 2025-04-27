from pydantic_settings import BaseSettings
import os
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings using Pydantic for validation and environment loading."""
    
    # JWT/Auth settings
    SECRET_KEY: str = "YOUR_SECRET_KEY"  # Default will be overridden by env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Alias JWT settings for compatibility
    JWT_SECRET: str = SECRET_KEY
    JWT_ALGORITHM: str = ALGORITHM
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Environment
    ENV: str = "development"
    
    # HTTPS Settings (optional)
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    
    # API
    API_PREFIX: str = "/api"
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    
    # Rate limiting
    RATE_LIMIT: int = 100  # requests per window
    RATE_WINDOW: int = 60  # time window in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create global settings object
settings = Settings()
