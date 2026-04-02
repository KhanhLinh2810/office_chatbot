from pydantic import BaseModel, Field


class RoomCreateRequest(BaseModel):
    number_room: str = Field(..., min_length=1)
    address: str
    capacity: int = Field(..., ge=1)
    status: int = Field(1, ge=0)


class RoomCreateResponse(BaseModel):
    id: int
    number_room: str
    address: str
    capacity: int
    status: int

    class Config:
        from_attributes = True