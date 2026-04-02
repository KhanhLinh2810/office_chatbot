import httpx
import msal
import requests

from app.core.settings import settings

class MicrosoftService:
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.authority = settings.MICROSOFT_AUTHORITY
        self.scopes = [settings.MICROSOFT_SCOPES]

        # Khởi tạo MSAL Confidential Client
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    def get_access_token(self):
        result = self.app.acquire_token_silent(self.scopes, account=None)
        
        if not result:
            # Nếu cache trống, yêu cầu token mới từ Microsoft
            result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Lỗi lấy token: {result.get('error_description')}")

    async def get_calendar_events(self, user_email):
        try:
            """Lấy lịch của một user cụ thể trong tổ chức"""
            token = self.get_access_token()
            # Đối với Service, bạn phải chỉ định email của user cần lấy lịch
            endpoint = f"https://graph.microsoft.com/v1.0/users/tuanna@mzcvn2.onmicrosoft.com/calendar/events"
            
            headers = {'Authorization': f'Bearer {token}'}
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                return f"Error: {response}"
            
        except Exception as e:
            return f"Exception: {str(e)}"