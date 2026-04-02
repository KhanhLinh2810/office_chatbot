from fastapi import APIRouter, Depends, HTTPException

from app.api.depend import SessionDep
from app.core.settings import settings
from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.users.create import UserCreateRequest, UserCreateResponse
from app.services import user_service
from app.utils.string import random_password
from app.modules import microsoft_service


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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password": data.password,
            "role": user.role,
            "status": user.status,
            "manager_id": user.manager_id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def delete(user_id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        if not current_user.role == 1:
            raise HTTPException(status_code=400, detail="permission_denied")
        
        user = await user_service.find_or_fail_by_id(session, user_id)
        if current_user.id == user.id:
            raise HTTPException(status_code=400, detail="permission_denied")
        await user_service.delete(session, user)
        
        return {
            "id": user.id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get-calendar")
async def get_calendar(session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        if not current_user.role == 1:
            raise HTTPException(status_code=400, detail="permission_denied")
        
        # Add logic to fetch calendar events for the current user
        calendar_events = await microsoft_service.get_calendar_events(current_user.email)

        return {
            "calendar_events": calendar_events
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))