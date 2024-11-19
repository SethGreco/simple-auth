from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql://postgres:postgres@db/postgres"
    JWT_SECRET_KEY: str = ""
    ALGO: str = ""
    ALLOWED_IP_ADDRESSES: list[str] = []
    CLIENT_BASE_URL: str = ""
    ENVIRONMENT: str = "local"


settings = Settings()
