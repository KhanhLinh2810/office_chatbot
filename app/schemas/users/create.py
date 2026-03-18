from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    email: str 
    password: str = Field(..., min_length=6, max_length=256, default="")

class UserCreateResponse (BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True