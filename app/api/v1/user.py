from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from httpx import request

from app.api.depend import SessionDep
from app.core.settings import settings
from app.schemas.users.create import UserCreateRequest
from app.services import user_service
from app.utils.string import random_password


router = APIRouter(tags=["user"])

@router.post("/")
async def create(data: UserCreateRequest, session: SessionDep):
    try:
        if not data.password:
            data.password = random_password(settings.RANDOM_PASSWORD_LENGTH)
        user = await user_service.create(
            session=session,
            email=data.email,
            password=data.password
        )
        return {
            "id": user.id,
            "email": user.email,
            "password": data.password,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))