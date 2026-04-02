from fastapi import APIRouter, Depends, HTTPException

from app.api.depend import SessionDep
from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.rooms.create import RoomCreateRequest
from app.schemas.rooms.update import RoomUpdate
from app.services.rooms import RoomService

router = APIRouter(tags=["rooms"])
room_service = RoomService()


@router.post("/", response_model=dict)
async def create_room(data: RoomCreateRequest, session: SessionDep, current_user: User = Depends(authenticate)):
    if current_user.role != 1:
        raise HTTPException(status_code=400, detail="permission_denied")

    room = await room_service.create(session, data)
    return {
        "id": room.id,
        "number_room": room.number_room,
        "address": room.address,
        "capacity": room.capacity,
        "status": room.status,
    }


@router.get("/")
async def get_rooms(session: SessionDep, current_user: User = Depends(authenticate)):
    await authenticate
    rooms = await room_service.find_all(session)
    return [
        {
            "id": r.id,
            "number_room": r.number_room,
            "address": r.address,
            "capacity": r.capacity,
            "status": r.status,
        }
        for r in rooms
    ]


@router.get("/{room_id}")
async def get_room(room_id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    await authenticate
    room = await room_service.find_or_fail_by_id(session, room_id)
    return {
        "id": room.id,
        "number_room": room.number_room,
        "address": room.address,
        "capacity": room.capacity,
        "status": room.status,
    }


@router.put("/{room_id}")
async def update_room(room_id: int, data: RoomUpdate, session: SessionDep, current_user: User = Depends(authenticate)):
    if current_user.role != 1:
        raise HTTPException(status_code=400, detail="permission_denied")

    room = await room_service.find_or_fail_by_id(session, room_id)
    updated_room = await room_service.update(session, room, data)
    return {
        "id": updated_room.id,
        "number_room": updated_room.number_room,
        "address": updated_room.address,
        "capacity": updated_room.capacity,
        "status": updated_room.status,
    }


@router.delete("/{room_id}")
async def delete_room(room_id: int, session: SessionDep, current_user: User = Depends(authenticate)):
    if current_user.role != 1:
        raise HTTPException(status_code=400, detail="permission_denied")

    room = await room_service.find_or_fail_by_id(session, room_id)
    await room_service.delete(session, room)
    return {"message": "room_deleted"}