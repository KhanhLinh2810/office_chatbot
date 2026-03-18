from fastapi import APIRouter, Depends, HTTPException

from app.api.depend import SessionDep
from app.core.settings import settings
from app.middleware import authenticate
from app.models.user import User
from app.schemas.users.create import UserCreateRequest
from app.services import user_service
from app.utils.string import random_password


router = APIRouter(tags=["user"])

@router.post("/")
async def create(data: UserCreateRequest, session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        if not current_user.role == 1:
            raise HTTPException(status_code=400, detail="permission_denied")
        
        if not data.password:
            data.password = random_password(settings.RANDOM_PASSWORD_LENGTH)
        user = await user_service.create(
            session=session,data=data
        )
        return {
            "id": user.id,
            "email": user.email,
            "password": data.password,
            "role": user.role,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))