from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI

from backend.adapters.scheduling.job_scheduler import Scheduler
from backend.main import lifespan


@pytest.mark.asyncio
async def test_lifespan_starts_and_stops_scheduler():
    scheduler_mock = Mock()
    with patch.object(
        Scheduler,
        "start_fetch_partner_deliveries_scheduled_job",
        return_value=scheduler_mock,
    ) as start_mock:
        async with lifespan(FastAPI()):
            start_mock.assert_called_once_with()
            scheduler_mock.shutdown.assert_not_called()
    scheduler_mock.shutdown.assert_called_once_with(wait=True)
