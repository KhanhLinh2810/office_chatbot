from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel, Field


class MeetingStatus(IntEnum):
    CANCELED = 0
    SCHEDULED = 1
    COMPLETED = 2


class MeetingType(IntEnum):
    IN_PERSON = 0
    ONLINE = 1
    HYBRID = 2


class MeetingCreateRequest(BaseModel):
    room_id: int | None = None
    title: str = Field(..., min_length=1)
    description: str
    start_at: datetime
    end_at: datetime
    status: MeetingStatus = Field(MeetingStatus.SCHEDULED)
    type: MeetingType = Field(MeetingType.IN_PERSON)
    link: str | None = None
    list_user_id: list[int] | None = None


class MeetingCreateResponse(BaseModel):
    id: int
    room_id: int
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    organizer_id: int
    status: MeetingStatus
    type: MeetingType
    link: str | None

    class Config:
        from_attributes = True