from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from app.api.depend import SessionDep
from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.meetings.create import MeetingCreateRequest
from app.schemas.meetings.update import MeetingUpdate
from app.services.meetings import MeetingService

router = APIRouter(tags=["meetings"])
meeting_service = MeetingService()


@router.post("/")
async def create_meeting(
    data: MeetingCreateRequest,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        meeting = await meeting_service.create(session, data, current_user)
        return {
            "id": meeting.id,
            "room_id": meeting.room_id,
            "title": meeting.title,
            "description": meeting.description,
            "start_at": meeting.start_at,
            "end_at": meeting.end_at,
            "organizer_id": meeting.organizer_id,
            "status": meeting.status,
            "type": meeting.type,
            "link": meeting.link,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_meetings(
    session: SessionDep,
    current_user: User = Depends(authenticate),
    start_at: datetime = Query(None),
    room_id: int = Query(None),
    include_my_meeting: bool = Query(False)
):
    meetings = await meeting_service.find_with_filters(session, start_at, room_id, include_my_meeting, current_user.id)
    return [
        {
            "id": m.id,
            "room_id": m.room_id,
            "title": m.title,
            "description": m.description,
            "start_at": m.start_at,
            "end_at": m.end_at,
            "organizer_id": m.organizer_id,
            "status": m.status,
            "type": m.type,
            "link": m.link,
        }
        for m in meetings
    ]


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    try:
        m = await meeting_service.find_or_fail_by_id(session, meeting_id)
        return {
            "id": m.id,
            "room_id": m.room_id,
            "title": m.title,
            "description": m.description,
            "start_at": m.start_at,
            "end_at": m.end_at,
            "organizer_id": m.organizer_id,
            "status": m.status,
            "type": m.type,
            "link": m.link,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    data: MeetingUpdate,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        meeting = await meeting_service.find_or_fail_by_id(session, meeting_id)
        updated = await meeting_service.update(session, meeting, data, current_user)
        return {
            "id": updated.id,
            "room_id": updated.room_id,
            "title": updated.title,
            "description": updated.description,
            "start_at": updated.start_at,
            "end_at": updated.end_at,
            "organizer_id": updated.organizer_id,
            "status": updated.status,
            "type": updated.type,
            "link": updated.link,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    session: SessionDep,
    current_user: User = Depends(authenticate),
):
    try:
        meeting = await meeting_service.find_or_fail_by_id(session, meeting_id)
        await meeting_service.delete(session, meeting, current_user)
        return {"id": meeting.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))