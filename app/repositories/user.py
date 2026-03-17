from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

class UserRepository:
    async def create_user(self, db: AsyncSession, user: User):
        db.add(user)
        await db.commit()
        
        await db.refresh(user)
        return user
    
    