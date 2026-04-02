from datetime import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.user import User
from app.repositories.meetings import MeetingRepository
from app.schemas.meetings.create import MeetingCreateRequest
from app.schemas.meetings.update import MeetingUpdate


class MeetingService:
    def __init__(self):
        self.meeting_repository = MeetingRepository()

    async def create(self, session: AsyncSession, data: MeetingCreateRequest, organizer: User):
        start = data.start_at
        end = data.end_at

        if end <= start:
            raise ValueError("end_before_start")

        if start.time() < time(9, 0) or start.time() >= time(17, 0):
            raise ValueError("start_out_of_business_hours")

        if end.time() > time(17, 0) or end.time() <= time(9, 0):
            raise ValueError("end_out_of_business_hours")

        length = (end - start).total_seconds() / 3600
        if length > 4:
            raise ValueError("meeting_too_long")

        meeting = Meeting(
            room_id=data.room_id,
            title=data.title,
            description=data.description,
            start_at=start,
            end_at=end,
            organizer_id=organizer.id,
            status=data.status,
            type=data.type,
            link=data.link,
        )

        return await self.meeting_repository.create(session, meeting)

    async def find_all(self, session: AsyncSession):
        return await self.meeting_repository.find_all(session)

    async def find_or_fail_by_id(self, session: AsyncSession, meeting_id: int):
        meeting = await self.meeting_repository.find_by_id(session, meeting_id)
        if not meeting:
            raise ValueError("meeting_not_found")
        return meeting

    async def update(self, session: AsyncSession, meeting: Meeting, data: MeetingUpdate, current_user: User):
        if meeting.organizer_id != current_user.id and current_user.role != 1:
            raise ValueError("permission_denied")

        start = data.start_at or meeting.start_at
        end = data.end_at or meeting.end_at

        if end <= start:
            raise ValueError("end_before_start")

        if start.time() < time(9, 0) or start.time() >= time(17, 0):
            raise ValueError("start_out_of_business_hours")

        if end.time() > time(17, 0) or end.time() <= time(9, 0):
            raise ValueError("end_out_of_business_hours")

        length = (end - start).total_seconds() / 3600
        if length > 4:
            raise ValueError("meeting_too_long")

        return await self.meeting_repository.update(session, meeting, data)

    async def delete(self, session: AsyncSession, meeting: Meeting, current_user: User):
        if meeting.organizer_id != current_user.id and current_user.role != 1:
            raise ValueError("permission_denied")

        return await self.meeting_repository.delete(session, meeting)