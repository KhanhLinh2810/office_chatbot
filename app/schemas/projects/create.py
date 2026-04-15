from pydantic import BaseModel, Field
from datetime import datetime


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    start_at: datetime
    end_at: datetime


class ProjectCreateResponse(BaseModel):
    id: int
    title: str
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
