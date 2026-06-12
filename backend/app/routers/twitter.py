from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.core.sse import sse_event
from app.models.twitter import TwitterGenerateRequest, TwitterSessionResponse
from app.services.session_store import session_store
from app.services.twitter_generator import TwitterContentGenerator

router = APIRouter(prefix="/api/twitter", tags=["twitter"])


@router.post("/sessions", response_model=TwitterSessionResponse)
def create_twitter_generation_session(payload: TwitterGenerateRequest):
    """Create a session so the frontend can use EventSource GET for SSE.

    EventSource is GET-only in the browser. This endpoint accepts the larger
    POST body first, then the frontend opens GET /sse/{session_id}.
    """
    session_id = session_store.create(payload)
    return TwitterSessionResponse(
        session_id=session_id,
        sse_url=f"/api/twitter/sse/{session_id}",
    )


@router.get("/sse/{session_id}")
def stream_twitter_content(session_id: str, request: Request):
    payload = session_store.get(session_id)

    if payload is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    settings = get_settings()

    def generate():
        try:
            yield sse_event(
                "start",
                {
                    "message": "Twitter content generation started",
                    "model": settings.kimi_model,
                },
            )

            generator = TwitterContentGenerator(settings)
            full_text = ""

            for token in generator.stream_generate(payload):
                full_text += token
                yield sse_event("token", {"token": token})

            yield sse_event("final", {"content": full_text})
            yield sse_event("done", {"done": True})

        except Exception as exc:
            yield sse_event("error", {"message": str(exc)})

        finally:
            session_store.delete(session_id)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
