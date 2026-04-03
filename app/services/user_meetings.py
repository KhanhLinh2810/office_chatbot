from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_meetings import UserMeeting
from app.repositories.user_meetings import UserMeetingRepository
from app.schemas.user_meetings.create import UserMeetingCreateRequest, UserMeetingItem
from app.schemas.user_meetings.update import UserMeetingUpdate
from app.services.meetings import MeetingService
from app.models.user import User
from app.services.user import UserService


class UserMeetingService:
    def __init__(self):
        self.user_meeting_repository = UserMeetingRepository()
        self.meeting_service = MeetingService()
        self.user_service = UserService()

    async def create_bulk(self, session: AsyncSession, data: UserMeetingCreateRequest, current_user: User):
        meeting = await self.meeting_service.find_or_fail_by_id(session, data.meeting_id)
        if meeting.organizer_id != current_user.id:
            existing_um = await self.user_meeting_repository.find_by_user_and_meeting(session, current_user.id, data.meeting_id)
            if not existing_um:
                raise ValueError("not_participant_or_organizer")
            allowed_roles = [0] 
        else: allowed_roles = [0, 1]
        
        results = []
        for item in data.participants:
            # Kiểm tra nếu đã tồn tại
            existing_u = await self.user_service.find_by_id(session, item.user_id)
            if not existing_u: 
                continue
            existing_um = await self.user_meeting_repository.find_by_user_and_meeting(session, item.user_id, data.meeting_id)
            if existing_um:
                # Nếu role khác và là organizer, cập nhật
                if existing_um.role != item.role and current_user.id == meeting.organizer_id:
                    update_data = UserMeetingUpdate(role=item.role)
                    updated = await self.update(session, existing_um, update_data)
                    results.append(updated)
            else:
                if item.role not in allowed_roles:
                    item.role = 0

                # Tạo mới với status=1
                user_meeting = UserMeeting(
                    user_id=item.user_id,
                    meeting_id=data.meeting_id,
                    role=item.role,
                    status=1,
                )
                created = await self.user_meeting_repository.create(session, user_meeting)
                results.append(created)

        return results

    async def create(self, session: AsyncSession, data: UserMeetingCreateRequest):
        user_meeting = UserMeeting(
            user_id=data.user_id,
            meeting_id=data.meeting_id,
            role=data.role,
            status=data.status,
        )
        return await self.user_meeting_repository.create(session, user_meeting)

    async def find_all(self, session: AsyncSession):
        return await self.user_meeting_repository.find_all(session)

    async def find_or_fail_by_id(self, session: AsyncSession, id: int):
        user_meeting = await self.user_meeting_repository.find_by_id(session, id)
        if not user_meeting:
            raise ValueError("user_meeting_not_found")
        return user_meeting

    async def update(self, session: AsyncSession, user_meeting: UserMeeting, data: UserMeetingUpdate):
        return await self.user_meeting_repository.update(session, user_meeting, data)

    async def delete(self, session: AsyncSession, user_meeting_id: str, current_user_id: str):
        um = await self.find_or_fail_by_id(session, user_meeting_id)
        if not um:
            raise ValueError("user_meeting_not_found")
        meeting = await self.meeting_service.find_or_fail_by_id(session, um.meeting_id)
        if meeting.organizer_id != current_user_id:
            raise ValueError("permission_denied")
        
        return await self.user_meeting_repository.delete(session, um)