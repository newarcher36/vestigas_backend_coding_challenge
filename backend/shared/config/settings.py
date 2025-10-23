import logging
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping

from apscheduler.triggers.cron import CronTrigger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    scheduler_cron: str = Field(validation_alias="SCHEDULER_CRON")
    database_url: str = Field(validation_alias="DATABASE_URL")
    logistics_a_url: str = Field(validation_alias="LOGISTICS_A_URL")
    logistics_b_url: str = Field(validation_alias="LOGISTICS_B_URL")
    source_a: str = Field(validation_alias="SOURCE_A")
    source_b: str = Field(validation_alias="SOURCE_B")
    site_id: str = Field(validation_alias="SITE_ID")
    http_timeout: float = Field(default=5.0, validation_alias="HTTP_TIMEOUT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="", case_sensitive=False)

    @field_validator("scheduler_cron")
    @classmethod
    def validate_cron(cls, cron_exp: str) -> str:
        try:
            CronTrigger.from_crontab(cron_exp)
        except Exception as e:
            raise ValueError(f"Invalid cron expression '{cron_exp}': {e}")
        return cron_exp

    @property
    def cron_trigger(self) -> CronTrigger:
        return CronTrigger.from_crontab(self.scheduler_cron, timezone="UTC")

    @property
    def partner_sources(self) -> set[str]:
        return {self.source_a, self.source_b}

    @property
    def partner_endpoints(self) -> Mapping[str, str]:
        return MappingProxyType({
            self.source_a: self.logistics_a_url,
            self.source_b: self.logistics_b_url,
        })


@lru_cache
def get_settings() -> Settings:
    return Settings()
