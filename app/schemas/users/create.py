from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str = Field(..., min_length=6, max_length=256)
    role: int = Field(0, ge=0, le=1)
    status: int = Field(1, ge=0, le=1)
    manager_id: int | None = None


class UserCreateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: int
    status: int
    manager_id: int | None

    class Config:
        from_attributes = True