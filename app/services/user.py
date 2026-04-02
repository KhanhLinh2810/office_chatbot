from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.users.create import UserCreateRequest
from app.utils.encryption import EncryptionUtils

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create(self, session: AsyncSession, data: UserCreateRequest):
        exitting_user = await self.user_repository.find_by_email(session, data.email)
        if exitting_user:
            raise ValueError("email_already_exists")

        hash_password = EncryptionUtils.hash_password(data.password)
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=hash_password,
            role=data.role,
            status=data.status,
            manager_id=data.manager_id
        )
        return await self.user_repository.create(session, user)
    
    async def find_or_fail_by_id(self, session: AsyncSession, id: int):
        user = await self.user_repository.find_by_id(session, id)
        if not user:
            raise ValueError("user_not_found")
        return user
    
    async def find_by_id(self, session: AsyncSession, id: int):
        return await self.user_repository.find_by_id(session, id)
