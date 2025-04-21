from pydantic import BaseModel, Field
from typing import List, Optional

class BulkQuestionUploadItem(BaseModel):
    test_name: str = Field(..., example="Midterm 1")
    question_text: str
    question_type: str = Field(..., example="mcq")
    options: Optional[str] = None  # JSON array string for MCQ, blank for others
    correct_answer: Optional[str] = None

class BulkQuestionUploadResponseItem(BaseModel):
    question_text: str
    test_name: str
    success: bool
    error: Optional[str] = None

class BulkQuestionUploadRequest(BaseModel):
    questions: List[BulkQuestionUploadItem]

class BulkQuestionUploadResponse(BaseModel):
    results: List[BulkQuestionUploadResponseItem]
