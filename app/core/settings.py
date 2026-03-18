from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # app_name: str = "Office Chatbot"
    BASE_URL: str = "http://localhost:8000"
    ADMIN_EMAIL: str = "admin@example.com"
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "office_chatbot"
    POSTGRES_SCHEMA: str = "public"
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_RECYCLE: int = 1800
    DEBUG: bool = False

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    GOOGLE_API_KEY: str = "abc123"
    GOOGLE_CLIENT_ID: str = "abc123"    
    GOOGLE_CLIENT_SECRET: str = "abc123"

    OPENAI_API_KEY: str = "abc123"
    OPENAI_BASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def GOOGLE_CLIENT_CONFIG(self):
        return {
            "web": {
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
    }
}

settings = Settings()