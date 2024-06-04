from typing import Any
import os
import secrets

from pydantic import BaseSettings, PostgresDsn, validator, EmailStr, AnyHttpUrl


class Settings(BaseSettings):
    """General"""

    APP_ENV: str
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/{API_VERSION}"
    PROJECT_NAME: str

    """Token"""
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPT_KEY = secrets.token_urlsafe(32)

    """Database"""
    DATABASE_HOST: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int | str
    DATABASE_NAME: str

    ASYNC_DATABASE_URI: PostgresDsn | None

    @validator("ASYNC_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )

    DB_POOL_SIZE = 83
    WEB_CONCURRENCY = 9
    POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

    """Redis"""
    REDIS_HOST: str
    REDIS_PORT: str

    """Initial"""
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    """CORS"""
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    """OAuth Providers"""
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET_ID: str
    KAKAO_REDIRECT_URI: str

    APPLE_CLIENT_ID: str
    APPLE_REDIRECT_URI: str
    APPLE_TEAM_ID: str
    APPLE_KEY_ID: str

    """AWS"""
    AWS_DEFAULT_REGION: str
    AWS_STORAGE_BUCKET_NAME: str
    APPLE_AUTH_KEY: str

    class Config:
        case_sensitive = True
        env_file = os.path.expanduser("~/.env")


settings = Settings()
