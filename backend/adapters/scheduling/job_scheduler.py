import logging
from typing import Iterable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.application.use_cases.fetch_deliveries import run_fetch_for_partners

logger = logging.getLogger("uvicorn.error")


def start_scheduler(partner_urls: Iterable[str], cron_trigger: CronTrigger) -> BackgroundScheduler:
    """Start the BackgroundScheduler using provided URLs and trigger."""
    urls = list(partner_urls)
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_fetch_for_partners,
        trigger=cron_trigger,
        kwargs={"urls": urls},
        id="partners-fetch",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")
    return scheduler
