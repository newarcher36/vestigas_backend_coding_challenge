from __future__ import annotations

from functools import lru_cache
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from pydantic import BaseModel, ConfigDict

from backend.shared.config.settings import get_settings


class JobConfig(BaseModel):
    id: str
    replace_existing: bool
    coalesce: bool
    max_instances: int
    jobstore: str
    name: str
    description: str
    trigger: BaseTrigger
    kwargs: dict[str, Any]

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


@lru_cache
def get_default_job_config() -> JobConfig:
    settings = get_settings()
    return JobConfig(
        id="partners-fetch",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        jobstore="default",
        name="partners-fetch-job",
        description="Fetch partner deliveries scheduled job.",
        trigger=settings.cron_trigger,
        kwargs={
            "site_id": settings.site_id,
            "partner_sources": settings.partner_sources,
        },
    )
