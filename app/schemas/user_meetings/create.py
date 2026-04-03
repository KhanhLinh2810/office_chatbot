from pydantic import BaseModel, Field
from typing import List


class UserMeetingItem(BaseModel):
    user_id: int
    role: int = Field(0, ge=0)


class UserMeetingCreateRequest(BaseModel):
    meeting_id: int
    participants: List[UserMeetingItem]


class UserMeetingCreateResponse(BaseModel):
    id: int
    user_id: int
    meeting_id: int
    role: int
    status: int

    class Config:
        from_attributes = True