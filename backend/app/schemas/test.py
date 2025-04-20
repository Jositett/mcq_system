from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class QuestionBase(BaseModel):
    question_text: str
    question_type: str  # MCQ, True/False, Theory
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

class TestBase(BaseModel):
    name: str
    batch_id: int
    scheduled_at: str | None = None  # ISO date string
    questions: List[QuestionBase]

class TestCreate(TestBase):
    pass

class TestResponse(TestBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

