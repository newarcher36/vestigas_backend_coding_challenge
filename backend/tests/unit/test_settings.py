import os
import pytest
from unittest.mock import patch
from apscheduler.triggers.cron import CronTrigger
from backend.shared.config.settings import Settings


@patch.dict(
    os.environ,
    {
        "POSTGRES_USER": "postgres-user",
        "POSTGRES_PASSWORD": "postgres-password",
        "POSTGRES_DB": "postgres-db",
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
    assert settings.postgres_user == "postgres-user"
    assert settings.postgres_password == "postgres-password"
    assert settings.postgres_db == "postgres-db"
    assert settings.postgres_host == "db"
    assert settings.postgres_port == 5432
    assert (
        settings.postgres_dsn
        == "postgresql+psycopg://postgres-user:postgres-password@db:5432/postgres-db"
    )
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
                             "POSTGRES_USER",
                             "POSTGRES_PASSWORD",
                             "POSTGRES_DB",
                             "SCHEDULER_CRON",
                             "LOGISTICS_A_URL",
                             "LOGISTICS_B_URL",
                             "SITE_ID",
                             "SOURCE_A",
                             "SOURCE_B",
                         ])
def test_settings_missing_required_field_raises(missing):
    env = {
        "POSTGRES_USER": "postgres-user",
        "POSTGRES_PASSWORD": "postgres-password",
        "POSTGRES_DB": "postgres-db",
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
        "POSTGRES_USER": "postgres-user",
        "POSTGRES_PASSWORD": "postgres-password",
        "POSTGRES_DB": "postgres-db",
        "SCHEDULER_CRON": "invalid cron",
        "LOGISTICS_A_URL": "http://a",
        "LOGISTICS_B_URL": "http://b",
        "SITE_ID": "any-site-id",
        "SOURCE_A": "source-a",
        "SOURCE_B": "source-b",
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
        "POSTGRES_USER": "postgres-user",
        "POSTGRES_PASSWORD": "postgres-password",
        "POSTGRES_DB": "postgres-db",
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
    assert settings.postgres_host == "db"
    assert settings.postgres_port == 5432
    assert settings.partner_sources == {"source-a", "source-b"}
    endpoints = settings.partner_endpoints
    assert set(endpoints.keys()) == {"source-a", "source-b"}
