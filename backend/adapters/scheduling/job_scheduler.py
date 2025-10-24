from __future__ import annotations

import logging
from functools import lru_cache
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends

from backend.adapters.repostory import JobsRepository, get_jobs_port
from backend.adapters.scheduling.job_status import JobStatus
from backend.adapters.scheduling.job_config import JobConfig, get_default_job_config
from backend.application.use_cases.fetch_deliveries import (
    FetchPartnerDeliveriesUseCase,
    get_fetch_partner_deliveries_use_case,
)
from backend.shared.utils.date_utils import Clock, get_utc_clock

logger = logging.getLogger("uvicorn.error")


class Scheduler:
    def __init__(self, fetch_partner_deliveries_use_case: FetchPartnerDeliveriesUseCase, clock: Clock,
                 job_config: JobConfig, job_repository: JobsRepository):
        self._fetch_deliveries_use_case = fetch_partner_deliveries_use_case
        self._clock = clock
        self._job_config = job_config
        self._job_repository = job_repository

    def start_fetch_partner_deliveries_scheduled_job(self) -> BackgroundScheduler:
        logger.info("Starting scheduler...")
        scheduler = BackgroundScheduler(timezone="UTC")
        job_config_kwargs = self._job_config.model_dump()
        scheduler.add_job(
            self._run_fetch_job,
            **job_config_kwargs,
        )
        scheduler.start()
        logger.info("Scheduler started.")
        return scheduler

    def _run_fetch_job(self, site_id: str, partner_sources: set[str]) -> None:
        """Invoke the fetch use case as the scheduled job."""
        utc_now = self._clock.get_utc_now()
        job_id = uuid4()
        self._job_repository.create_job(job_id, JobStatus.PROCESSING, self._clock.get_utc_now(), self._clock.get_utc_now(), {},None)
        logger.info("Job %s created at %s.", job_id, utc_now.isoformat())
        logger.info(
            "Fetching partner deliveries for site %s using sources %s (scheduled at %s).",
            site_id,
            sorted(partner_sources),
            utc_now.isoformat(),
        )
        deliveries = self._fetch_deliveries_use_case.fetch_partner_deliveries(site_id, utc_now, partner_sources)
        logger.info(
            "Fetched %d partner deliveries for site %s (scheduled at %s).",
            len(deliveries),
            site_id,
            utc_now.isoformat(),
        )


@lru_cache
def get_job_scheduler(
        fetch_partner_deliveries_use_case: FetchPartnerDeliveriesUseCase = Depends(get_fetch_partner_deliveries_use_case),
        clock: Clock = Depends(get_utc_clock),
        jobs_repository: JobsRepository = Depends(get_jobs_port)
) -> Scheduler:
    job_config: JobConfig = get_default_job_config()
    return Scheduler(fetch_partner_deliveries_use_case, clock, job_config, jobs_repository)
