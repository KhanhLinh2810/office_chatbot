import jwt
import datetime
import os

from app.core.settings import settings

class JWTUtils:
    @staticmethod
    def create_token(data: dict, secret_key: str = settings.JWT_SECRET_KEY, expires_delta: int = settings.JWT_EXPIRE_MINUTES):
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, secret_key: str = settings.JWT_SECRET_KEY):
        """
        Xác thực và giải mã JWT
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
            return payload 
        except jwt.ExpiredSignatureError:
            return "expired_token"
        except jwt.InvalidTokenError:
            return "invalid_token"