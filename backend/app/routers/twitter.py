from time import perf_counter

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.sse import sse_event
from app.models.twitter import TwitterGenerateRequest, TwitterSessionResponse
from app.services.session_store import session_store
from app.services.twitter_generator import TwitterContentGenerator

router = APIRouter(prefix="/api/twitter", tags=["twitter"])
logger = get_logger(__name__)


@router.post("/sessions", response_model=TwitterSessionResponse)
def create_twitter_generation_session(payload: TwitterGenerateRequest):
    """Create a session so the frontend can use EventSource GET for SSE.

    EventSource is GET-only in the browser. This endpoint accepts the larger
    POST body first, then the frontend opens GET /sse/{session_id}.
    """
    session_id = session_store.create(payload)
    logger.info(
        "session_created session_id=%s topic=%r tone=%s audience=%r language=%s count=%s max_chars=%s hashtags=%s",
        session_id,
        payload.topic[:80],
        payload.tone,
        payload.audience[:80],
        payload.language,
        payload.count,
        payload.max_chars,
        payload.include_hashtags,
    )
    return TwitterSessionResponse(
        session_id=session_id,
        sse_url=f"/api/twitter/sse/{session_id}",
    )


@router.get("/sse/{session_id}")
def stream_twitter_content(session_id: str, request: Request):
    payload = session_store.get(session_id)

    if payload is None:
        logger.warning("session_missing session_id=%s", session_id)
        raise HTTPException(status_code=404, detail="Session not found or expired")

    settings = get_settings()

    def generate():
        started_at = perf_counter()
        first_token_at: float | None = None
        token_count = 0
        try:
            logger.info("sse_started session_id=%s model=%s", session_id, settings.kimi_model)
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
                token_count += 1
                if first_token_at is None:
                    first_token_at = perf_counter()
                    logger.info(
                        "sse_first_token session_id=%s first_token_latency_ms=%d",
                        session_id,
                        int((first_token_at - started_at) * 1000),
                    )
                full_text += token
                yield sse_event("token", {"token": token})

            total_duration_ms = int((perf_counter() - started_at) * 1000)
            logger.info(
                "sse_completed session_id=%s token_chunks=%s content_chars=%s total_duration_ms=%s",
                session_id,
                token_count,
                len(full_text),
                total_duration_ms,
            )
            yield sse_event("final", {"content": full_text})
            yield sse_event("done", {"done": True})

        except Exception as exc:
            logger.exception("sse_failed session_id=%s error=%s", session_id, exc)
            yield sse_event("error", {"message": str(exc)})

        finally:
            session_store.delete(session_id)
            logger.info("session_deleted session_id=%s", session_id)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
)
