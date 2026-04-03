from datetime import datetime
from pydantic import BaseModel, Field


class MeetingCreateRequest(BaseModel):
    room_id: int | None = None
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    status: int = Field(1, ge=0)
    type: int = Field(0, ge=0)
    link: str | None = None


class MeetingCreateResponse(BaseModel):
    id: int
    room_id: int
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    organizer_id: int
    status: int
    type: int
    link: str | None

    class Config:
        from_attributes = True