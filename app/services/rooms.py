from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rooms import Room
from app.repositories.rooms import RoomRepository
from app.schemas.rooms.create import RoomCreateRequest
from app.schemas.rooms.update import RoomUpdate


class RoomService:
    def __init__(self):
        self.room_repository = RoomRepository()

    async def create(self, session: AsyncSession, data: RoomCreateRequest):
        room = Room(
            number_room=data.number_room,
            address=data.address,
            capacity=data.capacity,
            status=data.status,
        )
        return await self.room_repository.create(session, room)

    async def find_all(self, session: AsyncSession):
        return await self.room_repository.find_all(session)

    async def find_or_fail_by_id(self, session: AsyncSession, room_id: int):
        room = await self.room_repository.find_by_id(session, room_id)
        if not room:
            raise ValueError("room_not_found")
        return room

    async def update(self, session: AsyncSession, room: Room, data: RoomUpdate):
        return await self.room_repository.update(session, room, data)

    async def delete(self, session: AsyncSession, room: Room):
        return await self.room_repository.delete(session, room)