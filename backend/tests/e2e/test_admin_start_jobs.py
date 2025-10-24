from fastapi.testclient import TestClient

from backend.main import app


def test_admin_start_jobs_endpoint_returns_status_code():
    with TestClient(app) as client:
        response = client.post("/admin/start-jobs")

    assert response.status_code == 202
