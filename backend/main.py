import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.adapters.scheduling.job_scheduler import start_scheduler
from backend.shared.config.settings import Settings

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings
    scheduler = start_scheduler(settings.partner_urls(), settings.cron_trigger)

    yield

    try:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown complete.")
    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {e}")
    logger.info("Application shutdown complete.")


app = FastAPI(title="VESTIGAS Backend Challenge", lifespan=lifespan, root_path="/backend")

@app.get("/")
def root():
    return {"message": "Backend challenge scaffold is running"}
