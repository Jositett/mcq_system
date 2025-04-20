from pydantic import BaseModel
from typing import Optional

from datetime import date

from pydantic import ConfigDict

class AttendanceBase(BaseModel):
    student_id: int
    date: date  # Python date object
    status: str  # Present/Absent

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
