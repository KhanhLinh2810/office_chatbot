from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.users.update import UserUpdate

class UserRepository:
    async def create(self, db: AsyncSession, user: User):
        db.add(user)
        await db.commit()
        
        await db.refresh(user)
        return user
    
    async def find_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def find_by_id(self, db: AsyncSession, id: int) -> User | None:
        query = select(User).where(User.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
        
    async def update(self, db: AsyncSession, user: User, data: UserUpdate):
        update_data = data.model_dump(exclude_unset=True) 
        if not update_data:
            return user 

        if "password" in update_data:
            pass 

        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user) 
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def delete(self, db: AsyncSession, user: User):
        await db.delete(user)
        await db.commit()
    
    