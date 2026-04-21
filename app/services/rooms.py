from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rooms import Room
from app.repositories.rooms import RoomRepository
from app.repositories.meetings import MeetingRepository
from app.repositories.user_meetings import UserMeetingRepository
from app.schemas.rooms.create import RoomCreateRequest
from app.schemas.rooms.update import RoomUpdate


class RoomService:
    def __init__(self):
        self.room_repository = RoomRepository()
        self.meeting_repository = MeetingRepository()
        self.user_meeting_repository = UserMeetingRepository()

    async def create(self, session: AsyncSession, data: RoomCreateRequest):
        room = Room(
            number_room=data.number_room,
            address=data.address,
            capacity=data.capacity,
            status=data.status,
        )
        return await self.room_repository.create(session, room)

    async def find_all(self, session: AsyncSession, status=None):
        return await self.room_repository.find_all(session, status)

    async def find_available_rooms(self, session: AsyncSession, start_at, end_at, status=None):
        return await self.room_repository.find_available_rooms(session, start_at, end_at, status)

    async def find_or_fail_by_id(self, session: AsyncSession, room_id: int):
        room = await self.room_repository.find_by_id(session, room_id)
        if not room:
            raise ValueError("room_not_found")
        return room

    async def update(self, session: AsyncSession, room: Room, data: RoomUpdate):
        return await self.room_repository.update(session, room, data)

    async def delete(self, session: AsyncSession, room: Room):
        # Get all meetings for this room
        meetings = await self.meeting_repository.find_by_room_id(session, room.id)
        
        # Delete user_meetings for each meeting
        for meeting in meetings:
            await self.user_meeting_repository.delete_by_meeting_id(session, meeting.id)
        
        # Delete all meetings for this room
        await self.meeting_repository.delete_by_room_id(session, room.id)
        
        # Delete the room
        return await self.room_repository.delete(session, room)