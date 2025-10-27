from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import Mock, patch

from backend.adapters.scheduling import job_scheduler
from backend.adapters.scheduling.job_config import JobConfig
from backend.adapters.scheduling.job_scheduler import Scheduler
from backend.adapters.scheduling.job_status import JobStatus
from backend.domain.stats import Stats


def test_scheduler_run_fetch_partner_deliveries_job_schedules_and_starts():
    fetch_use_case = Mock()
    store_use_case = Mock()
    clock = Mock()
    job_config = Mock(spec=JobConfig)
    job_config.model_dump.return_value = {"id": "123"}
    jobs_repository = Mock()

    scheduler = Scheduler(fetch_use_case, store_use_case, clock, job_config, jobs_repository)

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
        **{"id": "123"},
    )
    mock_scheduler_instance.start.assert_called_once_with()
    assert background_scheduler is mock_scheduler_instance


def test_scheduler_run_fetch_job_invokes_use_case_with_expected_arguments():
    fetch_use_case = Mock()
    store_use_case = Mock()
    clock = Mock()
    job_config = Mock()
    jobs_repository = Mock()

    scheduled_time = datetime(2024, 1, 15, tzinfo=timezone.utc)
    clock.get_utc_now.return_value = scheduled_time
    stats_result = Stats.for_partner("source-a")
    unified_deliveries = []
    fetch_use_case.fetch_partner_deliveries.return_value = (stats_result, unified_deliveries)

    partner_sources = {"source-a"}

    scheduler = Scheduler(fetch_use_case, store_use_case, clock, job_config, jobs_repository)

    scheduler._run_fetch_job("site-456", partner_sources)

    assert clock.get_utc_now.call_count == 2
    fetch_use_case.fetch_partner_deliveries.assert_called_once_with("site-456", "source-a")

    jobs_repository.create_job.assert_called_once()
    call_args = jobs_repository.create_job.call_args
    job_id, status, created_at, updated_at, input_payload = call_args.args
    assert isinstance(job_id, UUID)
    assert status == JobStatus.PROCESSING
    assert created_at == scheduled_time
    assert updated_at == scheduled_time
    assert input_payload == {"site_id": "site-456", "date": scheduled_time.isoformat()}

    store_use_case.store.assert_called_once_with(job_id, unified_deliveries)
    jobs_repository.update_job_stats.assert_called_once_with(job_id, stats_result, scheduled_time, None)
