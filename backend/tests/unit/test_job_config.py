from apscheduler.triggers.cron import CronTrigger

from backend.adapters.scheduling.job_config import JobConfig


def test_job_config_model_dump_includes_partner_sources_in_kwargs():
    trigger = CronTrigger.from_crontab("0 6 * * *")
    partner_sources = {"source-a", "source-b"}
    job_config = JobConfig(
        id="partners-fetch",
        replace_existing=True,
        coalesce=False,
        max_instances=2,
        jobstore="memory",
        name="partners-fetch-job",
        description="Fetch partner deliveries scheduled job.",
        trigger=trigger,
        kwargs={"site_id": "site-123", "partner_sources": partner_sources},
    )

    job_dict = job_config.model_dump()
    assert job_dict == {
        "id": "partners-fetch",
        "replace_existing": True,
        "coalesce": False,
        "max_instances": 2,
        "jobstore": "memory",
        "name": "partners-fetch-job",
        "description": "Fetch partner deliveries scheduled job.",
        "trigger": trigger,
        "kwargs": {"site_id": "site-123", "partner_sources": partner_sources},
    }
