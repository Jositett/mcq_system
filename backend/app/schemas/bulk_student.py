from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date

class BulkStudentUploadItem(BaseModel):
    full_name: str = Field(..., example="John Doe")
    email: EmailStr
    roll_number: Optional[str] = None
    dob: Optional[date] = None
    batch_name: str = Field(..., example="Batch A")

class BulkStudentUploadResponseItem(BaseModel):
    full_name: str
    email: EmailStr
    batch_name: str
    success: bool
    error: Optional[str] = None

class BulkStudentUploadRequest(BaseModel):
    students: List[BulkStudentUploadItem]

class BulkStudentUploadResponse(BaseModel):
    results: List[BulkStudentUploadResponseItem]
