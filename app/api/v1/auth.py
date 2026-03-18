from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from httpx import request

from app.api.depend import SessionDep
from app.schemas.users.create import UserCreateRequest
from app.schemas.auth.login import UserLoginRequest
from app.services import user_service, auth_service
from app.core.settings import settings
from app.callbacks import google_callback
from app.modules import cache_service
from app.utils.jwt import JWTUtils


router = APIRouter(tags=["auth"])

@router.post("/register")
async def register(data: UserCreateRequest, session: SessionDep):
    try:
        user = await user_service.create(
            session=session,
            email=data.email,
            password=data.password
        )
        return {
            "id": user.id,
            "email": user.email,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: UserLoginRequest, session: SessionDep):
    try:
        user = await auth_service.authenticate(
            session=session,
            email=data.email,
            password=data.password
        )
        return {
            "access_token": JWTUtils.create_token({"user_id": user.id}),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/google")
async def authorize_google():
    try:
        scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid' 
        ]
        flow = Flow.from_client_config(
            settings.GOOGLE_CLIENT_CONFIG,
            scopes=scopes,
            redirect_uri=settings.BASE_URL + "/api/v1/auth/google/callback"
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline', # lấy refresh_token
            prompt='consent',      # hiện màn hình hỏi quyền
            include_granted_scopes='true'
        )
        print("Authorization URL:", authorization_url)

        cache_service.set(state, flow.code_verifier)

        # Điều hướng người dùng tới trang của Google
        return RedirectResponse(url=authorization_url)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/google/callback")
async def authorize_google_callback(request: Request, session: SessionDep, code: str = None, error: str = None, state: str = None   ):
    if error:
        raise HTTPException(status_code=401, detail=str(f"Người dùng từ chối cấp quyền: {error}"))
    if not code:
        raise HTTPException(status_code=400, detail="Không tìm thấy mã code từ Google")
    try:
        code_verifier = cache_service.get(state)
        user = await google_callback.handle_google_callback(session, code, state, code_verifier)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))