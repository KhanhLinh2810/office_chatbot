from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_projects import UserProject


class UserProjectRepository:
    async def create(self, db: AsyncSession, user_project: UserProject):
        db.add(user_project)
        await db.commit()
        await db.refresh(user_project)
        return user_project

    async def find_all(self, db: AsyncSession):
        query = select(UserProject)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, id: int):
        query = select(UserProject).where(UserProject.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_user_id(self, db: AsyncSession, user_id: int):
        query = select(UserProject).where(UserProject.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def delete_by_user_id(self, db: AsyncSession, user_id: int):
        query = delete(UserProject).where(UserProject.user_id == user_id)
        await db.execute(query)
        await db.commit()