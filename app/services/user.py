from app.models.user import User
from app.repositories.user import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create_user(self, session, email, password):
        user = User(email=email, password=password)        
        return await self.user_repository.create_user(session, user)
    