from pydantic import BaseModel
from typing import Optional, List

from pydantic import ConfigDict

class InstructorBase(BaseModel):
    user_id: int
    department: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class InstructorCreate(InstructorBase):
    pass

class InstructorResponse(InstructorBase):
    id: int
    batches: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)

