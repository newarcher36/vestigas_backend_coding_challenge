from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, ConfigDict

from backend.shared.config.settings import get_settings, Settings


class PostgresConfig(BaseModel):
    postgres_dsn: str

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


@lru_cache
def get_postgres_config() -> PostgresConfig:
    settings: Settings = get_settings()
    database_url = (
            f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
    return PostgresConfig(postgres_dsn=database_url)
