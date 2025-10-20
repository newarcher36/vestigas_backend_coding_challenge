import os
import pytest
from unittest.mock import patch

from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from backend.main import app
import backend.main as main_mod


class DummyScheduler:
    def __init__(self):
        self.shutdown_called = False

    def shutdown(self, wait=False):
        self.shutdown_called = True


@patch.dict(os.environ, {
    "DATABASE_URL": "postgresql://user:pw@db:5432/db",
    "SCHEDULER_CRON": "0 * * * *",
    "LOGISTICS_A_URL": "http://a",
    "LOGISTICS_B_URL": "http://b",
}, clear=True)
@pytest.mark.asyncio
async def test_app_lifespan_starts_and_shuts_scheduler(monkeypatch):
    scheduler_instance = DummyScheduler()

    def fake_start_scheduler(partner_urls, cron_trigger):
        return scheduler_instance

    # Patch the start_scheduler used by the app module
    monkeypatch.setattr(main_mod, "start_scheduler", fake_start_scheduler)
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.get("/")
            assert r.status_code == 200

    # After client context exits, lifespan cleanup should call shutdown
    assert scheduler_instance.shutdown_called is True
