from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.users.create import UserCreateRequest
from app.schemas.users.update import UserUpdate
from app.utils.encryption import EncryptionUtils

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create(self, session: AsyncSession, data: UserCreateRequest):
        if await self.check_email_exists(session, data.email):
            raise ValueError("email_already_exists")

        hash_password = EncryptionUtils.hash_password(data.password)
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=hash_password,
            role=data.role,
            status=data.status,
            manager_id=data.manager_id if data.manager_id != 0 else None
        )
        return await self.user_repository.create(session, user)
    
    async def find_or_fail_by_id(self, session: AsyncSession, id: int):
        user = await self.user_repository.find_by_id(session, id)
        if not user:
            raise ValueError("user_not_found")
        return user
    
    async def find_by_id(self, session: AsyncSession, id: int):
        return await self.user_repository.find_by_id(session, id)

    async def find_by_ids(self, session: AsyncSession, ids: list[int]):
        return await self.user_repository.find_by_ids(session, ids)

    async def find_all(self, session: AsyncSession, email: str | None = None):
        return await self.user_repository.find_all(session, email)
    
    async def check_email_exists(self, session: AsyncSession, email: str, exclude_user_id: int | None = None):
        existing_user = await self.user_repository.find_by_email(session, email)
        if existing_user and (exclude_user_id is None or existing_user.id != exclude_user_id):
            return True
        return False
    
    async def update(self, session: AsyncSession, user: User, data: UserUpdate):
        # Check email uniqueness if email is being updated
        if data.email and await self.check_email_exists(session, data.email, exclude_user_id=user.id):
            raise ValueError("email_already_exists")
        
        # Handle manager_id = 0 as None
        if hasattr(data, 'manager_id') and data.manager_id == 0:
            data.manager_id = None
        
        return await self.user_repository.update(session, user, data)
    
    async def reset_password(self, session: AsyncSession, user: User, new_password: str):
        hashed_password = EncryptionUtils.hash_password(new_password)
        update_data = UserUpdate(password=hashed_password)
        return await self.update(session, user, update_data)
    
    async def delete(self, session: AsyncSession, user: User):
        return await self.user_repository.delete(session, user)
