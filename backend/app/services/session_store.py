from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4

from app.models.twitter import TwitterGenerateRequest


class SessionStore:
    """Small in-memory store for POST -> SSE session flow.

    Good for learning/local demo. For production, replace this with Redis,
    Postgres, or another shared store because multiple server instances cannot
    share this in-memory dictionary.
    """

    def __init__(self, ttl_minutes: int = 20):
        self._items: dict[str, tuple[TwitterGenerateRequest, datetime]] = {}
        self._lock = Lock()
        self._ttl = timedelta(minutes=ttl_minutes)

    def create(self, payload: TwitterGenerateRequest) -> str:
        session_id = uuid4().hex
        expires_at = datetime.now(timezone.utc) + self._ttl

        with self._lock:
            self._cleanup_locked()
            self._items[session_id] = (payload, expires_at)

        return session_id

    def get(self, session_id: str) -> TwitterGenerateRequest | None:
        with self._lock:
            self._cleanup_locked()
            item = self._items.get(session_id)

        if item is None:
            return None

        payload, _ = item
        return payload

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._items.pop(session_id, None)

    def _cleanup_locked(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [key for key, (_, expires_at) in self._items.items() if expires_at < now]
        for key in expired:
            self._items.pop(key, None)


session_store = SessionStore()
