from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_meetings import UserMeeting
from app.schemas.user_meetings.update import UserMeetingUpdate


class UserMeetingRepository:
    async def create(self, db: AsyncSession, user_meeting: UserMeeting):
        db.add(user_meeting)
        await db.commit()
        await db.refresh(user_meeting)
        return user_meeting

    async def create_many(self, db: AsyncSession, user_meetings: list[UserMeeting]):
        if not user_meetings:
            return []
        db.add_all(user_meetings)
        await db.commit()
        return user_meetings

    async def find_all(self, db: AsyncSession):
        query = select(UserMeeting)
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, id: int):
        query = select(UserMeeting).where(UserMeeting.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, user_meeting: UserMeeting, data: UserMeetingUpdate):
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return user_meeting

        for field, value in update_data.items():
            setattr(user_meeting, field, value)

        db.add(user_meeting)
        await db.commit()
        await db.refresh(user_meeting)
        return user_meeting

    async def find_by_user_and_meeting(self, db: AsyncSession, user_id: int, meeting_id: int):
        query = select(UserMeeting).where(UserMeeting.user_id == user_id, UserMeeting.meeting_id == meeting_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_meeting_id(self, db: AsyncSession, meeting_id: int):
        query = select(UserMeeting).where(UserMeeting.meeting_id == meeting_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def delete(self, db: AsyncSession, user_meeting: UserMeeting):
        await db.delete(user_meeting)
        await db.commit()