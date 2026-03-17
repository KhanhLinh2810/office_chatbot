

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, AsyncGenerator

from app.loader.database import sessionmanager

sessionmanager.init_db()
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in sessionmanager.get_session():
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]