import os
import pytest
from unittest.mock import patch
from apscheduler.triggers.cron import CronTrigger
from backend.shared.config.settings import Settings


@patch.dict(os.environ, {
    "DATABASE_URL": "postgresql://user1:pass1@host:5432/db1",
    "SCHEDULER_CRON": "0 * * * *",
    "LOGISTICS_A_URL": "http://a",
    "LOGISTICS_B_URL": "http://b",
}, clear=True)
def test_settings_reads_all_fields():
    settings = Settings()
    assert settings.database_url == "postgresql://user1:pass1@host:5432/db1"
    assert isinstance(settings.cron_trigger, CronTrigger)
    urls = settings.partner_urls()
    assert urls == {"http://a", "http://b"}


@pytest.mark.parametrize(
    "missing",
    [
        "DATABASE_URL",
        "SCHEDULER_CRON",
    ],
)
def test_settings_missing_required_field_raises(missing):
    env = {
        "DATABASE_URL": "postgresql://user:pw@db:5432/db",
        "SCHEDULER_CRON": "0 * * * *",
    }
    env.pop(missing, None)
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(Exception):
            Settings()


def test_settings_invalid_cron_raises():
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pw@db:5432/db", "SCHEDULER_CRON": "invalid cron"}, clear=True):
        with pytest.raises(Exception):
            Settings()
