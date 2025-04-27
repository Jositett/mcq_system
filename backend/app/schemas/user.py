from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic import ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    role: str
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    gender: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    password: Optional[str] = None
    profile_picture: Optional[str] = None

from pydantic import ConfigDict

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

