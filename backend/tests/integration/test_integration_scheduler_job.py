from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
import respx
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from httpx import Response

from backend.adapters.outbound.partners.fetch_partner_deliveries_http_adapter import (
    PartnerDeliveriesHttpAdapter,
)
from backend.adapters.outbound.partners.http_config import HttpConfig
from backend.adapters.scheduling.job_config import JobConfig
from backend.adapters.scheduling.job_scheduler import Scheduler
from backend.application.use_cases.fetch_deliveries import FetchPartnerDeliveriesUseCase
from backend.shared.utils.date_utils import Clock


@pytest.fixture
def partner_endpoints() -> dict[str, str]:
    return {
        "Partner A": "https://partner-a.test",
        "Partner B": "https://partner-b.test",
    }


@pytest.fixture
def http_config(partner_endpoints: dict[str, str]) -> HttpConfig:
    return HttpConfig(timeout=0.1, endpoints=partner_endpoints)


@pytest.fixture
def fetch_partner_deliveries_adapter(http_config: HttpConfig) -> PartnerDeliveriesHttpAdapter:
    return PartnerDeliveriesHttpAdapter(http_config=http_config)


@pytest.fixture
def partner_sources(partner_endpoints: dict[str, str]) -> set[str]:
    return set(partner_endpoints.keys())


@pytest.fixture
def fetch_use_case(fetch_partner_deliveries_adapter: PartnerDeliveriesHttpAdapter) -> FetchPartnerDeliveriesUseCase:
    return FetchPartnerDeliveriesUseCase(fetch_partner_deliveries_port=fetch_partner_deliveries_adapter)


@pytest.fixture
def clock() -> Mock:
    return Mock(spec=Clock)


@pytest.fixture
def jobs_repository() -> Mock:
    return Mock()


@pytest.fixture
def job_config_factory(partner_sources: set[str]):
    def _factory(trigger_time: datetime) -> JobConfig:
        return JobConfig(
            id="partners-fetch",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            jobstore="default",
            name="partners-fetch-job",
            description="Fetch partner deliveries scheduled job.",
            trigger=DateTrigger(run_date=trigger_time),
            kwargs={"site_id": "site-123", "partner_sources": partner_sources},
        )

    return _factory


@pytest.fixture
def scheduler_factory(
    fetch_use_case: FetchPartnerDeliveriesUseCase,
    clock: Mock,
    jobs_repository: Mock,
):
    def _factory(job_config: JobConfig) -> Scheduler:
        return Scheduler(fetch_use_case, clock, job_config, jobs_repository)

    return _factory


def wait_for_job_completion(background_scheduler: BackgroundScheduler, *, timeout: float = 3.0) -> None:
    """Block until the scheduled job runs once or the timeout expires."""
    completion_signal = threading.Event()
    captured_exceptions: list[BaseException] = []

    def on_job_event(event):
        if event.exception:
            captured_exceptions.append(event.exception)
        completion_signal.set()

    background_scheduler.add_listener(on_job_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    try:
        if not completion_signal.wait(timeout=timeout):
            pytest.fail("Scheduled job did not complete within timeout")

        if captured_exceptions:
            pytest.fail(f"Job raised: {captured_exceptions[0]}")
    finally:
        background_scheduler.remove_listener(on_job_event)
        background_scheduler.shutdown(wait=False)


def test_scheduler_fetch_job_triggers_partner_http_calls(
    partner_endpoints: dict[str, str],
    job_config_factory,
    scheduler_factory,
    clock: Mock,
):
    trigger_time = datetime.now(timezone.utc) + timedelta(milliseconds=200)
    clock.get_utc_now.return_value = trigger_time

    job_config = job_config_factory(trigger_time)
    scheduler = scheduler_factory(job_config)

    payload_a = {"deliveryId": "DEL-001-A"}
    payload_b = {"deliveryId": "DEL-002-B"}

    with respx.mock(assert_all_called=True) as respx_mock:
        route_partner_a = respx_mock.post(partner_endpoints["Partner A"]).mock(
            return_value=Response(200, json=payload_a),
        )
        route_partner_b = respx_mock.post(partner_endpoints["Partner B"]).mock(
            return_value=Response(200, json=payload_b),
        )

        background_scheduler = scheduler.start_fetch_partner_deliveries_scheduled_job()

        wait_for_job_completion(background_scheduler)

        assert route_partner_a.called
        assert route_partner_b.called
