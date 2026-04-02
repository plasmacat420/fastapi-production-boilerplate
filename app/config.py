from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI Boilerplate"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # JWT
    SECRET_KEY: str = "change-this-in-production-use-256-bit-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env"}


settings = Settings()
