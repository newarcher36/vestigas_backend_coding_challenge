import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette import status

from backend.adapters.scheduling.job_scheduler import Scheduler, get_job_scheduler
from fastapi import Depends

logger = logging.getLogger("uvicorn.error")


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

