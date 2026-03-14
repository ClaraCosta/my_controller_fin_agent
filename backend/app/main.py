from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.routes import api_router
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging, get_logger
from backend.app.db.seed import seed_initial_data

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application_starting", extra={"app_env": settings.app_env})
    seed_initial_data()
    yield
    logger.info("application_stopping")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")
app.include_router(api_router)

