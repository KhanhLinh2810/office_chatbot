from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Project
from app.repositories.projects import ProjectRepository
from app.schemas.projects.create import ProjectCreateRequest
from app.schemas.projects.update import ProjectUpdate


class ProjectService:
    def __init__(self):
        self.project_repository = ProjectRepository()

    async def create(self, session: AsyncSession, data: ProjectCreateRequest):
        if data.end_at <= data.start_at:
            raise ValueError("end_before_start")

        project = Project(
            title=data.title,
            start_at=data.start_at,
            end_at=data.end_at,
        )
        return await self.project_repository.create(session, project)

    async def find_all(self, session: AsyncSession):
        return await self.project_repository.find_all(session)

    async def find_or_fail_by_id(self, session: AsyncSession, id: int):
        project = await self.project_repository.find_by_id(session, id)
        if not project:
            raise ValueError("project_not_found")
        return project

    async def update(self, session: AsyncSession, project: Project, data: ProjectUpdate):
        if data.end_at and data.start_at and data.end_at <= data.start_at:
            raise ValueError("end_before_start")

        return await self.project_repository.update(session, project, data)

    async def delete(self, session: AsyncSession, project: Project):
        return await self.project_repository.delete(session, project)
