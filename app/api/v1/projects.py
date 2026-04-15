from fastapi import APIRouter, Depends, HTTPException

from app.api.depend import SessionDep
from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.projects.create import ProjectCreateRequest
from app.schemas.projects.update import ProjectUpdate
from app.services.projects import ProjectService

router = APIRouter(tags=["projects"])
project_service = ProjectService()


@router.post("/")
async def create_project(
    data: ProjectCreateRequest,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        project = await project_service.create(session, data)
        return {
            "id": project.id,
            "title": project.title,
            "start_at": project.start_at,
            "end_at": project.end_at,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_projects(session: SessionDep, current_user: User = Depends(authenticate)):
    projects = await project_service.find_all(session)
    return [
        {
            "id": p.id,
            "title": p.title,
            "start_at": p.start_at,
            "end_at": p.end_at,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in projects
    ]


@router.get("/{id}")
async def get_project(id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        project = await project_service.find_or_fail_by_id(session, id)
        return {
            "id": project.id,
            "title": project.title,
            "start_at": project.start_at,
            "end_at": project.end_at,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id}")
async def update_project(
    id: int,
    data: ProjectUpdate,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        if current_user.role != 1:
            raise HTTPException(status_code=403, detail="permission_denied")

        project = await project_service.find_or_fail_by_id(session, id)
        updated = await project_service.update(session, project, data)
        return {
            "id": updated.id,
            "title": updated.title,
            "start_at": updated.start_at,
            "end_at": updated.end_at,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}")
async def delete_project(
    id: int,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        if current_user.role != 1:
            raise HTTPException(status_code=403, detail="permission_denied")

        project = await project_service.find_or_fail_by_id(session, id)
        await project_service.delete(session, project)
        return {"message": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
