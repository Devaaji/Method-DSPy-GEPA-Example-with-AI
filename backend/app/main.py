from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.routers.health import router as health_router
from app.routers.twitter import router as twitter_router

configure_logging()
settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(twitter_router)

logger.info(
    "backend_configured app=%s frontend_url=%s provider_base=%s model=%s",
    settings.app_name,
    settings.frontend_url,
    settings.kimi_base_url,
    settings.kimi_model,
)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }
