from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import chat, document, health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.security import validate_api_keys

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    validate_api_keys()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Assistant médical intelligent basé sur une architecture RAG.",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


app.include_router(health.router)
app.include_router(document.router)
app.include_router(chat.router)
