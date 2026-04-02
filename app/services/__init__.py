
from app.services.user import UserService
from app.services.auth import AuthService
from app.services.rooms import RoomService
from app.services.meetings import MeetingService

user_service = UserService()
auth_service = AuthService()
room_service = RoomService()
meeting_service = MeetingService()