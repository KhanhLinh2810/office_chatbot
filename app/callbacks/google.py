
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.core.settings import settings
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.users.update import UserUpdate

class GoogleService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def handle_google_callback(self, session, code, state, code_verifier: str = None) -> User:
        scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid' 
        ]
        flow = Flow.from_client_config(
            settings.GOOGLE_CLIENT_CONFIG,
            scopes=scopes,
            redirect_uri=settings.BASE_URL + "/api/v1/auth/google/callback",
            state=state
        )
        if code_verifier:
            flow.code_verifier = code_verifier

        flow.fetch_token(code=code)
        credentials = flow.credentials

        access_token = credentials.token
        refresh_token = credentials.refresh_token

        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()
        user_email = user_info.get('email')

        user = await self.user_repository.find_by_email(session, user_email)
        if not user:
            raise ValueError("user_not_found")
        await self.user_repository.update(session, user=user, data=UserUpdate(google_refresh_token=refresh_token, google_access_token=access_token))
        
        return user