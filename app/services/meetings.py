from datetime import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.user import User
from app.repositories.meetings import MeetingRepository
from app.schemas.meetings.create import MeetingCreateRequest
from app.schemas.meetings.update import MeetingUpdate
from app.services.rooms import RoomService


class MeetingService:
    def __init__(self):
        self.meeting_repository = MeetingRepository()
        self.room_service = RoomService()

    async def create(self, session: AsyncSession, data: MeetingCreateRequest, organizer: User):
        start = data.start_at.replace(tzinfo=None)
        end = data.end_at.replace(tzinfo=None)

        if end <= start:
            raise ValueError("end_before_start")

        if start.time() < time(9, 0) or start.time() >= time(17, 0):
            raise ValueError("start_out_of_business_hours")

        if end.time() > time(17, 0) or end.time() <= time(9, 0):
            raise ValueError("end_out_of_business_hours")

        length = (end - start).total_seconds() / 3600
        if length > 4:
            raise ValueError("meeting_too_long")

        # Conditional requirements for type
        if data.type in [0, 2] and data.room_id is None:
            raise ValueError("room_id_required_for_meeting_in_person_or_hybrid")

        if data.type in [1, 2] and (data.link is None or not data.link.strip()):
            raise ValueError("link_required_for_meeting_online_or_hybrid")

        # Check room availability for in-person and hybrid meetings
        if data.type in [0, 2]:  # 0: in-person, 2: hybrid
            # Check if room exists and is available
            room = await self.room_service.find_or_fail_by_id(session, data.room_id)
            if room.status != 1:
                raise ValueError("room_not_available")
            
            # Check for time conflicts
            if await self.meeting_repository.check_room_conflict(session, data.room_id, start, end):
                raise ValueError("room_time_conflict")

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

    async def find_with_filters(self, session: AsyncSession, start_at=None, room_id=None, include_my_meeting=False, current_user_id=None):
        if start_at is not None and getattr(start_at, 'tzinfo', None) is not None:
            start_at = start_at.replace(tzinfo=None)
        return await self.meeting_repository.find_with_filters(session, start_at, room_id, include_my_meeting, current_user_id)

    async def find_or_fail_by_id(self, session: AsyncSession, meeting_id: int):
        meeting = await self.meeting_repository.find_by_id(session, meeting_id)
        if not meeting:
            raise ValueError("meeting_not_found")
        return meeting

    async def update(self, session: AsyncSession, meeting: Meeting, data: MeetingUpdate, current_user: User):
        if meeting.organizer_id != current_user.id and current_user.role != 1:
            raise ValueError("permission_denied")

        if data.start_at:
            data.start_at = data.start_at.replace(tzinfo=None)
        if data.end_at:
            data.end_at = data.end_at.replace(tzinfo=None)

        start = data.start_at or meeting.start_at.replace(tzinfo=None)
        end = data.end_at or meeting.end_at.replace(tzinfo=None)

        if end <= start:
            raise ValueError("end_before_start")

        if start.time() < time(9, 0) or start.time() >= time(17, 0):
            raise ValueError("start_out_of_business_hours")

        if end.time() > time(17, 0) or end.time() <= time(9, 0):
            raise ValueError("end_out_of_business_hours")

        length = (end - start).total_seconds() / 3600
        if length > 4:
            raise ValueError("meeting_too_long")

        # Conditional requirements for type
        meeting_type = data.type if data.type is not None else meeting.type
        room_id = data.room_id if data.room_id is not None else meeting.room_id
        link = data.link if data.link is not None else meeting.link

        if meeting_type in [0, 2] and room_id is None:
            raise ValueError("room_id_required_for_meeting_in_person_or_hybrid")

        if meeting_type in [1, 2] and (link is None or not link.strip()):
            raise ValueError("link_required_for_meeting_online_or_hybrid")

        # Check room availability for in-person and hybrid meetings
        if meeting_type in [0, 2]:  # 0: in-person, 2: hybrid
            # Check if room exists and is available
            room = await self.room_service.find_or_fail_by_id(session, room_id)
            if room.status != 1:
                raise ValueError("room_not_available")
            
            # Check for time conflicts (exclude current meeting)
            if await self.meeting_repository.check_room_conflict(session, room_id, start, end, exclude_meeting_id=meeting.id):
                raise ValueError("room_time_conflict")

        return await self.meeting_repository.update(session, meeting, data)

    async def delete(self, session: AsyncSession, meeting: Meeting, current_user: User):
        if meeting.organizer_id != current_user.id and current_user.role != 1:
            raise ValueError("permission_denied")

        return await self.meeting_repository.delete(session, meeting)