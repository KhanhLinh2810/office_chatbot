from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.schemas.meetings.update import MeetingUpdate


class MeetingRepository:
    async def create(self, db: AsyncSession, meeting: Meeting):
        db.add(meeting)
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def find_all(self, db: AsyncSession):
        query = select(Meeting)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, meeting_id: int):
        query = select(Meeting).where(Meeting.id == meeting_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, meeting: Meeting, data: MeetingUpdate):
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return meeting

        if "link" not in update_data and meeting.link is not None:
            # link optional; no change if not provided
            pass

        for field, value in update_data.items():
            setattr(meeting, field, value)

        db.add(meeting)
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def delete(self, db: AsyncSession, meeting: Meeting):
        await db.delete(meeting)
        await db.commit()