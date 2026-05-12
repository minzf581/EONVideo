from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EONVideo AI Short Video System"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://eonvideo:eonvideo@localhost:5432/eonvideo"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
