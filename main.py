from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from app.api.router import api_router

security = HTTPBearer()
app = FastAPI(
    title="Office Chatbot API", 
    version="1.0",
    dependencies=[Depends(security)]
)

app.include_router(api_router, prefix="/api")