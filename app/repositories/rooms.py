from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rooms import Room
from app.schemas.rooms.update import RoomUpdate


class RoomRepository:
    async def create(self, db: AsyncSession, room: Room):
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room

    async def find_all(self, db: AsyncSession):
        query = select(Room)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, room_id: int):
        query = select(Room).where(Room.id == room_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, room: Room, data: RoomUpdate):
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return room

        for field, value in update_data.items():
            setattr(room, field, value)

        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room

    async def delete(self, db: AsyncSession, room: Room):
        await db.delete(room)
        await db.commit()