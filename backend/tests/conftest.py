import os

import pytest


def pytest_sessionstart(session):
    os.environ.update({
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
    })
