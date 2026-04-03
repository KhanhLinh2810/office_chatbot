from sqlalchemy import and_, or_, select
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
    
    async def check_room_conflict(self, db: AsyncSession, room_id: int, start_at, end_at, exclude_meeting_id: int | None = None):
        query = select(Meeting).where(
            and_(
                Meeting.room_id == room_id,
                Meeting.status != 2,  # Not canceled
                or_(
                    and_(Meeting.start_at < end_at, Meeting.end_at > start_at),
                )
            )
        )
        if exclude_meeting_id:
            query = query.where(Meeting.id != exclude_meeting_id)
        
        result = await db.execute(query)
        conflicting_meetings = result.scalars().all()
        return len(conflicting_meetings) > 0