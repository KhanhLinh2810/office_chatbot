from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    email: str
    password: str

class UserCreateResponse (BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True