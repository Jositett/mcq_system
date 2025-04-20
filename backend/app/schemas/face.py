from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class FaceImageBase(BaseModel):
    image_data: str  # base64-encoded image
    embedding: Optional[str] = None  # JSON string or comma-separated floats
    created_at: date

class FaceImageCreate(FaceImageBase):
    pass

from pydantic import ConfigDict

class FaceImageResponse(FaceImageBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
