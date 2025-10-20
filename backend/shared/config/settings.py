import logging
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    scheduler_cron: str = Field(validation_alias="SCHEDULER_CRON")
    logistics_a_url: Optional[str] = Field(validation_alias="LOGISTICS_A_URL")
    logistics_b_url: Optional[str] = Field(validation_alias="LOGISTICS_B_URL")

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

    def partner_urls(self) -> set[str]:
        urls = set()
        if self.logistics_a_url:
            urls.add(self.logistics_a_url)
        if self.logistics_b_url:
            urls.add(self.logistics_b_url)
        return urls
