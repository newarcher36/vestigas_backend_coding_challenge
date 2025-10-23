import os
import pytest
from unittest.mock import patch
from apscheduler.triggers.cron import CronTrigger
from backend.shared.config.settings import Settings


@patch.dict(
    os.environ,
    {
        "DATABASE_URL": "any-database-url",
        "SCHEDULER_CRON": "0 * * * *",
        "LOGISTICS_A_URL": "http://a",
        "LOGISTICS_B_URL": "http://b",
        "SITE_ID": "any-site-id",
        "HTTP_TIMEOUT": "7.5",
        "SOURCE_A": "source-a",
        "SOURCE_B": "source-b",
    },
    clear=True,
)
def test_settings_reads_all_fields_from_environment():
    settings = Settings()
    assert settings.database_url == "any-database-url"
    assert isinstance(settings.cron_trigger, CronTrigger)
    endpoints = settings.partner_endpoints
    assert set(endpoints.keys()) == {"source-a", "source-b"}
    assert endpoints["source-a"] == "http://a"
    assert endpoints["source-b"] == "http://b"
    assert settings.partner_sources == {"source-a", "source-b"}
    assert settings.site_id == "any-site-id"
    assert settings.http_timeout == 7.5
    assert settings.source_a == "source-a"
    assert settings.source_b == "source-b"


@pytest.mark.parametrize("missing",
                         [
                             "DATABASE_URL",
                             "SCHEDULER_CRON",
                             "LOGISTICS_A_URL",
                             "LOGISTICS_B_URL",
                             "SITE_ID",
                             "SOURCE_A",
                             "SOURCE_B",
                         ])
def test_settings_missing_required_field_raises(missing):
    env = {
        "DATABASE_URL": "any-database-url",
        "SCHEDULER_CRON": "0 * * * *",
        "LOGISTICS_A_URL": "http://a",
        "LOGISTICS_B_URL": "http://b",
        "SITE_ID": "any-site-id",
        "SOURCE_A": "source-a",
        "SOURCE_B": "source-b",
    }
    env.pop(missing, None)
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(Exception) as exc_info:
            Settings()
        assert missing in str(exc_info.value)

@patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql://user:pw@db:5432/db",
        "SCHEDULER_CRON": "invalid cron",
    },
    clear=True,
)
def test_settings_invalid_cron_raises():
    with pytest.raises(ValueError) as exc_info:
        Settings()
    assert "Invalid cron expression" in str(exc_info.value)


@patch.dict(
    os.environ,
    {
        "DATABASE_URL": "any-database-url",
        "SCHEDULER_CRON": "0 * * * *",
        "LOGISTICS_A_URL": "http://a",
        "LOGISTICS_B_URL": "http://b",
        "SITE_ID": "any-site-id",
        "SOURCE_A": "source-a",
        "SOURCE_B": "source-b",
    },
    clear=True,
)
def test_settings_http_timeout_defaults_to_five_seconds():
    settings = Settings()
    assert settings.http_timeout == 5.0
    assert settings.partner_sources == {"source-a", "source-b"}
    endpoints = settings.partner_endpoints
    assert set(endpoints.keys()) == {"source-a", "source-b"}
