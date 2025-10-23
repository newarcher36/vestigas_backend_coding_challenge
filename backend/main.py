import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.adapters.scheduling.job_scheduler import Scheduler

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started.")
    scheduler = Scheduler
    bg_scheduler = scheduler.start_fetch_partner_deliveries_scheduled_job()
    yield
    bg_scheduler.shutdown(wait=True)
    logger.info("Scheduler shutdown complete.")
    logger.info("Application shutdown complete.")


app = FastAPI(title="VESTIGAS Backend Challenge", lifespan=lifespan, root_path="/backend")

@app.get("/")
def root():
    return {"message": "Backend challenge scaffold is running"}
