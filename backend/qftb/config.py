from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET_KEY: str
    ALGO: str
    ALLOWED_IP_ADDRESSES: list[str]
    CLIENT_BASE_URL: str
    ENVIRONMENT: str


settings = Settings()
