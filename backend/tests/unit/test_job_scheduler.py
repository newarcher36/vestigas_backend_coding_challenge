from datetime import datetime, timezone
from unittest.mock import Mock, patch

from backend.adapters.scheduling import job_scheduler
from backend.adapters.scheduling.job_config import JobConfig
from backend.adapters.scheduling.job_scheduler import Scheduler


def test_scheduler_run_fetch_partner_deliveries_job_schedules_and_starts():
    fetch_use_case = Mock()
    clock = Mock()
    job_config = Mock(spec=JobConfig)
    job_config.model_dump.return_value = {"id" : "123"}

    scheduler = Scheduler(fetch_use_case, clock, job_config)

    mock_scheduler_instance = Mock()

    with patch.object(
        job_scheduler,
        "BackgroundScheduler",
        return_value=mock_scheduler_instance,
    ) as mock_scheduler_cls:
        background_scheduler = scheduler.start_fetch_partner_deliveries_scheduled_job()

    mock_scheduler_cls.assert_called_once_with(timezone="UTC")
    job_config.model_dump.assert_called_once_with()
    mock_scheduler_instance.add_job.assert_called_once_with(
        scheduler._run_fetch_job,
        **{"id" : "123"},
    )
    mock_scheduler_instance.start.assert_called_once_with()
    assert background_scheduler is mock_scheduler_instance


def test_scheduler_run_fetch_job_invokes_use_case_with_expected_arguments():
    fetch_use_case = Mock()
    clock = Mock()
    job_config = Mock()

    scheduler = Scheduler(fetch_use_case, clock, job_config)

    scheduled_time = datetime(2024, 1, 15, tzinfo=timezone.utc)
    clock.get_utc_now.return_value = scheduled_time
    fetch_use_case.fetch_partner_deliveries.return_value = []

    partner_sources = {"source-a"}

    scheduler._run_fetch_job("site-456", partner_sources)

    clock.get_utc_now.assert_called_once_with()
    fetch_use_case.fetch_partner_deliveries.assert_called_once_with("site-456", scheduled_time, partner_sources)
