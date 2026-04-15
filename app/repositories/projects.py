from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.schemas.projects.update import ProjectUpdate


class ProjectRepository:
    async def create(self, db: AsyncSession, project: Project):
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    async def find_all(self, db: AsyncSession):
        query = select(Project)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, id: int):
        query = select(Project).where(Project.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, project: Project, data: ProjectUpdate):
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return project

        for field, value in update_data.items():
            setattr(project, field, value)

        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    async def delete(self, db: AsyncSession, project: Project):
        await db.delete(project)
        await db.commit()
