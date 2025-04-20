from pydantic import BaseModel, EmailStr
from typing import Optional

from pydantic import ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

from pydantic import ConfigDict

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

