from fastapi import APIRouter, HTTPException

from app.api.depend import SessionDep
from app.schemas.users.create import UserCreateRequest
from app.services import user_service


router = APIRouter(tags=["auth"])

@router.post("/register")
async def register(data: UserCreateRequest, session: SessionDep):
    try:
        print("Registering user with email:", data)
        user = await user_service.create_user(
            session=session,
            email=data.email,
            password=data.password
        )
        return user

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login():
    return {"message": "User logged in successfully"}