from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NOCFLOW_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NOC Flow Cloud API"
    app_version: str = "0.1.0-alpha"
    environment: Literal["development", "test", "staging", "production"] = "development"
    database_url: str = "postgresql+psycopg://nocflow:nocflow@localhost:5432/nocflow"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4200"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
