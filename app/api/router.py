from fastapi import APIRouter

from app.middleware import authenticate
from app.api.v1 import user, auth

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", dependencies=[authenticate])
api_router.include_router(auth.router, prefix="/v1/auth")