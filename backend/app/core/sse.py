import json
from typing import Any


def sse_event(event: str, data: dict[str, Any]) -> str:
    """Return one valid SSE event block.

    SSE format requires a blank line at the end. Without \n\n, the browser
    may keep buffering and EventSource will not emit the event.
    """
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
