import asyncio
from datetime import datetime, timedelta, timezone

import pytest
import respx
from apscheduler.triggers.date import DateTrigger
from httpx import Response

from backend.adapters.scheduling.job_scheduler import start_scheduler


@pytest.mark.asyncio
async def test_scheduler_triggers_http_calls():
    # Force an immediate one-shot trigger so the real scheduler runs the job now
    cron_trigger = DateTrigger(run_date=datetime.now(timezone.utc) + timedelta(milliseconds=50))
    partner_urls = {"http://example.test/a", "http://example.test/b"}

    with respx.mock(assert_all_called=True) as respx_mock:
        route_a = respx_mock.post("http://example.test/a").mock(return_value=Response(200, text="ok-a"))
        route_b = respx_mock.post("http://example.test/b").mock(return_value=Response(200, text="ok-b"))

        scheduler = start_scheduler(partner_urls, cron_trigger)
        await asyncio.wait_for(
            wait_until(lambda: route_a.called and route_b.called),
            timeout=5
        )
        scheduler.shutdown(wait=False)

async def wait_until(condition, check_interval=0.05):
    while not condition():
        await asyncio.sleep(check_interval)