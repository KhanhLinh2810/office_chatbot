from pydantic import BaseModel
from typing import Optional


class UserMeetingUpdate(BaseModel):
    role: Optional[int] = None
    status: Optional[int] = None