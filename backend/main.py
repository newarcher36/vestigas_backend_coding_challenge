import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, Query
from starlette import status

from backend.adapters.repostory.jobs.job_repository import get_jobs_port
from backend.adapters.repostory.unified_deliveries.unified_delivery_repository import (
    get_unified_deliveries_port,
)
from backend.adapters.scheduling.job_scheduler import Scheduler, get_job_scheduler
from backend.adapters.scheduling.job_status import JobStatus
from backend.ports.jobs_port import JobsPort
from backend.ports.unified_deliveries_port import UnifiedDeliveriesPort

logger = logging.getLogger("uvicorn.error")

MAX_PAGE_SIZE = 100


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started.")
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(title="VESTIGAS Backend Challenge", lifespan=lifespan, root_path="/backend")

@app.get("/")
def root():
    return {"message": "Backend challenge scaffold is running"}


@app.post("/admin/start-jobs", status_code=status.HTTP_202_ACCEPTED)
def start_scheduled_jobs(scheduler: Scheduler = Depends(get_job_scheduler)):
    logger.info("Request to start scheduled jobs received.")
    scheduler.start_fetch_partner_deliveries_scheduled_job()


def _isoformat(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


@app.get("/deliveries/jobs")
def list_jobs(
    limit: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    jobs_port: JobsPort = Depends(get_jobs_port),
):
    items, total = jobs_port.list_jobs(limit=limit, offset=offset)
    formatted = []
    for item in items:
        status_raw = item.get("status")
        if isinstance(status_raw, JobStatus):
            status_value = status_raw.value.lower()
        elif isinstance(status_raw, str):
            status_value = status_raw.lower()
        else:
            status_value = None

        formatted.append(
            {
                "jobId": item.get("jobId"),
                "status": status_value,
                "createdAt": _isoformat(item.get("createdAt")),
                "updatedAt": _isoformat(item.get("updatedAt")),
                "input": item.get("input", {}),
                "stats": item.get("stats") or {},
                "error": item.get("error"),
            },
        )
    return {
        "items": formatted,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/deliveries")
def list_deliveries(
    limit: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    deliveries_port: UnifiedDeliveriesPort = Depends(get_unified_deliveries_port),
):
    items, total = deliveries_port.list_deliveries(limit=limit, offset=offset)
    formatted: list[dict[str, Any]] = []
    for item in items:
        formatted.append(
            {
                "id": item.get("id"),
                "supplier": item.get("supplier"),
                "deliveredAt": item.get("deliveredAt"),
                "status": item.get("status"),
                "signed": item.get("signed"),
                "siteId": item.get("siteId"),
                "source": item.get("source"),
                "deliveryScore": item.get("deliveryScore"),
            },
        )
    return {
        "items": formatted,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
