from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    APP_NAME: str = "aegis-backend"
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    NEO4J_URI: str | None = None
    NEO4J_USER: str | None = None
    NEO4J_PASSWORD: str | None = None
    QDRANT_URL: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-pro" # Default, can be overridden by env
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    FRONTEND_ORIGIN: AnyHttpUrl = "http://localhost:3000"
    BACKEND_ORIGIN: str = "http://localhost:8000"
    REPOS_STORAGE_PATH: str = "/app/storage/repos"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
