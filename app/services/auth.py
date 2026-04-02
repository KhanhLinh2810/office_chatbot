from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.encryption import EncryptionUtils

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def authenticate(self, session, email, password):
        print(f"Authenticating user with email: {email}")
        user = await self.user_repository.find_by_email(session, email)
        if not user:
            raise ValueError("user_not_found")
        if not EncryptionUtils.verify_password(password, user.password):
            raise ValueError("invalid_password")
        return user
