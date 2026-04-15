
from app.services.user import UserService
from app.services.auth import AuthService
from app.services.rooms import RoomService
from app.services.meetings import MeetingService
from app.services.user_meetings import UserMeetingService
from app.services.projects import ProjectService

user_service = UserService()
auth_service = AuthService()
room_service = RoomService()
meeting_service = MeetingService()
user_meeting_service = UserMeetingService()
project_service = ProjectService()