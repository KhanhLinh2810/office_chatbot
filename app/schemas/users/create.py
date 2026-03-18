from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    email: str 
    password: str = Field(..., min_length=6, max_length=256, default="")
    role: int = Field(..., ge=0, le=1, default=0)

class UserCreateResponse (BaseModel):
    id: int
    email: str
    role: int

    class Config:
        from_attributes = True