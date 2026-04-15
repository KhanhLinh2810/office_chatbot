from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field


class MeetingStatus(IntEnum):
    CANCELED = 0
    SCHEDULED = 1
    COMPLETED = 2


class MeetingType(IntEnum):
    IN_PERSON = 0
    ONLINE = 1
    HYBRID = 2


class MeetingUpdate(BaseModel):
    room_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    type: Optional[MeetingType] = None
    link: Optional[str] = None