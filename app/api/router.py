from fastapi import APIRouter, Depends

from app.middleware.authenticate import authenticate
from app.api.v1 import user, auth

api_router = APIRouter()

api_router.include_router(user.router, prefix="/v1/users", dependencies=[Depends(authenticate)])
api_router.include_router(auth.router, prefix="/v1/auth")