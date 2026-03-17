from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # app_name: str = "Office Chatbot"
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

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()