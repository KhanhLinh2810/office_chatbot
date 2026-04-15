from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    class Config:
        from_attributes = True
