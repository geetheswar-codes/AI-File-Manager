from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    """

    # ----------------------------
    # Application
    # ----------------------------
    APP_NAME: str = "AI File Management Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # ----------------------------
    # Database
    # ----------------------------
    DATABASE_URL: str

    # ----------------------------
    # Security
    # ----------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()