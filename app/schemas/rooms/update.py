from pydantic import BaseModel
from typing import Optional


class RoomUpdate(BaseModel):
    number_room: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[int] = None