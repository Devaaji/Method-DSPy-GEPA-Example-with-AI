from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "default_provider": settings.ai_provider,
        "default_model": settings.provider_model(),
        "supported_providers": list(settings.supported_providers()),
    }
