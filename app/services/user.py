from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.encryption import EncryptionUtils

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create(self, session, email, password):
        exitting_user = await self.user_repository.find_by_email(session, email)
        if exitting_user:
            raise ValueError("email_already_exists")

        hash_password = EncryptionUtils.hash_password(password)
        user = User(email=email, password=hash_password)        
        return await self.user_repository.create(session, user)