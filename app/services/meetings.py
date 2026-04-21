from datetime import time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.user import User
from app.models.user_meetings import UserMeeting
from app.repositories.meetings import MeetingRepository
from app.repositories.user_meetings import UserMeetingRepository
from app.schemas.meetings.create import MeetingCreateRequest
from app.schemas.meetings.update import MeetingUpdate
from app.services.rooms import RoomService
from app.services.user import UserService


class MeetingService:
    def __init__(self):
        self.meeting_repository = MeetingRepository()
        self.room_service = RoomService()
        self.user_service = UserService()
        self.user_meeting_repository = UserMeetingRepository()

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

        created_meeting = await self.meeting_repository.create(session, meeting)

        if data.list_user_id:
            user_ids = [uid for uid in set(data.list_user_id) if uid != organizer.id]
            users = await self.user_service.find_by_ids(session, user_ids)
            user_meetings = [
                UserMeeting(
                    user_id=user.id,
                    meeting_id=created_meeting.id,
                    role=0,
                    status=1,
                )
                for user in users
            ]
            await self.user_meeting_repository.create_many(session, user_meetings)

        return created_meeting

    async def get_meeting_detail(self, session: AsyncSession, meeting_id: int):
        meeting = await self.find_or_fail_by_id(session, meeting_id)
        user_meetings = await self.user_meeting_repository.find_by_meeting_id(session, meeting_id)
        print("User Meetings:", user_meetings)  # Debugging statement
        user_ids = [um.user_id for um in user_meetings]
        users = await self.user_service.find_by_ids(session, user_ids)
        print("Users:", users)  # Debugging statement
        user_dict = {u.id: u for u in users}
        participants = [
            {
                "user_id": um.user_id,
                "first_name": user_dict[um.user_id].first_name,
                "last_name": user_dict[um.user_id].last_name,
                "email": user_dict[um.user_id].email,
            }
            for um in user_meetings if um.user_id in user_dict
        ]
        print("Participants:", participants)  # Debugging statement
        return meeting, participants

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

        updated_meeting = await self.meeting_repository.update(session, meeting, data)

        # Handle user_meetings updates
        if data.list_user_id or data.list_delete_user_id:
            current_user_meetings = await self.user_meeting_repository.find_by_meeting_id(session, meeting.id)
            current_user_ids = {um.user_id for um in current_user_meetings}

            # Add new users
            if data.list_user_id:
                new_user_ids = set(data.list_user_id) - current_user_ids - {meeting.organizer_id}
                if new_user_ids:
                    users = await self.user_service.find_by_ids(session, list(new_user_ids))
                    user_meetings = [
                        UserMeeting(
                            user_id=user.id,
                            meeting_id=meeting.id,
                            role=0,
                            status=1,
                        )
                        for user in users
                    ]
                    await self.user_meeting_repository.create_many(session, user_meetings)

            # Delete users
            if data.list_delete_user_id:
                delete_user_ids = set(data.list_delete_user_id) & current_user_ids
                if delete_user_ids:
                    for user_id in delete_user_ids:
                        um = next((um for um in current_user_meetings if um.user_id == user_id), None)
                        if um:
                            await self.user_meeting_repository.delete(session, um)

        return updated_meeting

    async def delete(self, session: AsyncSession, meeting: Meeting, current_user: User):
        if meeting.organizer_id != current_user.id and current_user.role != 1:
            raise ValueError("permission_denied")

        # Delete all user_meetings for this meeting
        await self.user_meeting_repository.delete_by_meeting_id(session, meeting.id)
        
        # Delete the meeting
        return await self.meeting_repository.delete(session, meeting)