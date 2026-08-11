"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Project Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"

    # API Keys (set in .env)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    SHODAN_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "sentinel-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
