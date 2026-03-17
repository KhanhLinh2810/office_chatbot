from fastapi import APIRouter
from .v1 import user, auth

api_router = APIRouter()

# api_router.include_router(user.router, prefix="/users")
api_router.include_router(auth.router, prefix="/v1/auth")