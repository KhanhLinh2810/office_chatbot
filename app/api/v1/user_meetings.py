from fastapi import APIRouter, Depends, HTTPException

from app.api.depend import SessionDep
from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.user_meetings.create import UserMeetingCreateRequest
from app.schemas.user_meetings.update import UserMeetingUpdate
from app.services.user_meetings import UserMeetingService

router = APIRouter(tags=["user_meetings"])
user_meeting_service = UserMeetingService()


@router.post("/")
async def create_user_meeting(
    data: UserMeetingCreateRequest,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        ums = await user_meeting_service.create_bulk(session, data, current_user)
        return [
            {
                "id": um.id,
                "user_id": um.user_id,
                "meeting_id": um.meeting_id,
                "role": um.role,
                "status": um.status,
            }
            for um in ums
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_user_meetings(session: SessionDep, current_user: User = Depends(authenticate)):
    ums = await user_meeting_service.find_all(session)
    return [
        {
            "id": u.id,
            "user_id": u.user_id,
            "meeting_id": u.meeting_id,
            "role": u.role,
            "status": u.status,
        }
        for u in ums
    ]


@router.get("/{id}")
async def get_user_meeting(id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        um = await user_meeting_service.find_or_fail_by_id(session, id)
        return {
            "id": um.id,
            "user_id": um.user_id,
            "meeting_id": um.meeting_id,
            "role": um.role,
            "status": um.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# @router.put("/{id}")
# async def update_user_meeting(
#     id: int,
#     data: UserMeetingUpdate,
#     session: SessionDep,
#     current_user: User = Depends(authenticate),
# ):
#     try:
#         if current_user.role != 1:
#             raise HTTPException(status_code=400, detail="permission_denied")

#         um = await user_meeting_service.find_or_fail_by_id(session, id)
#         updated = await user_meeting_service.update(session, um, data)
#         return {
#             "id": updated.id,
#             "user_id": updated.user_id,
#             "meeting_id": updated.meeting_id,
#             "role": updated.role,
#             "status": updated.status,
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}")
async def delete_user_meeting(
    id: int,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        await user_meeting_service.delete(session, id, current_user.id)
        return {"id": id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))