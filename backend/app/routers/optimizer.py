from fastapi import APIRouter

from app.prompts.twitter import load_optimized_prompt_data

router = APIRouter(prefix="/api/optimizer", tags=["optimizer"])


@router.get("/latest")
def get_latest_optimizer_artifact():
    artifact = load_optimized_prompt_data()
    if artifact is None:
        return {"available": False}

    return {"available": True, "artifact": artifact}
