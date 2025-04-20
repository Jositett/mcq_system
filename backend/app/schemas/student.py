from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from pydantic import ConfigDict

class StudentBase(BaseModel):
    user_id: int
    batch_id: int
    roll_number: str | None = None
    dob: date | None = None  # ISO date string
    model_config = ConfigDict(from_attributes=True)

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    attendance: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)

