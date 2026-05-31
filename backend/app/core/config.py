from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Weeeek API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://weeeek:weeeek@localhost:5432/weeeek",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    jwt_secret: str = Field(default="change-me-in-production", validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 8

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

