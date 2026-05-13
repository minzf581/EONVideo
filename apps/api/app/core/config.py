from __future__ import annotations

import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EONVideo AI Short Video System"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://eonvideo:eonvideo@localhost:5432/eonvideo"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_origin_regex: str = r"https://.*\.up\.railway\.app"
    hot_api_base_url: str = ""
    hot_api_key: str = ""
    wechat_source_config: list[dict[str, Any]] = []
    manual_seed_keywords: str = ""
    finance_news_rss_urls: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("wechat_source_config", mode="before")
    @classmethod
    def parse_wechat_source_config(cls, value: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
        if isinstance(value, str):
            if not value.strip():
                return []
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return []
            return parsed if isinstance(parsed, list) else []
        return value

    @property
    def manual_seed_keyword_list(self) -> list[str]:
        return [item.strip() for item in self.manual_seed_keywords.split(",") if item.strip()]

    @property
    def finance_news_rss_url_list(self) -> list[str]:
        return [item.strip() for item in self.finance_news_rss_urls.split(",") if item.strip()]


settings = Settings()
