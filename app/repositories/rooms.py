from sqlalchemy import select, exists, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rooms import Room
from app.models.meetings import Meeting
from app.schemas.rooms.update import RoomUpdate


class RoomRepository:
    async def create(self, db: AsyncSession, room: Room):
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room

    async def find_all(self, db: AsyncSession, status=None):
        query = select(Room)
        if status is not None:
            query = query.where(Room.status == status)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_available_rooms(self, db: AsyncSession, start_at, end_at, status=None):
        # Subquery to check for overlapping meetings
        overlapping_meetings = select(Meeting.id).where(
            and_(
                Meeting.room_id == Room.id,
                Meeting.start_at < end_at,
                Meeting.end_at > start_at
            )
        )
        query = select(Room).where(not_(exists(overlapping_meetings)))
        if status is not None:
            query = query.where(Room.status == status)
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