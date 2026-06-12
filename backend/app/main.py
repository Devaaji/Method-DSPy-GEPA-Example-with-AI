from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.health import router as health_router
from app.routers.twitter import router as twitter_router

settings = get_settings()

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


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }
