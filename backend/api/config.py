from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET_KEY: str
    ALGO: str
    ALLOWED_IP_ADDRESSES: list


settings = Settings()
