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
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    # ----------------------------
    # Database
    # ----------------------------
    DATABASE_URL: str

    AI_RUNTIME: str = "ollama"
    AI_MODEL: str = "qwen2.5:3b"
    AI_MAX_CONTEXT_LENGTH: int = 4096
    AI_SERVER_URL: str = "http://127.0.0.1:11434"

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
