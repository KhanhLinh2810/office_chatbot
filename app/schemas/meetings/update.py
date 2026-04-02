from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MeetingUpdate(BaseModel):
    room_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[int] = Field(default=None, ge=0)
    type: Optional[int] = Field(default=None, ge=0)
    link: Optional[str] = None