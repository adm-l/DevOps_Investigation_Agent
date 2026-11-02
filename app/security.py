import hmac
import time
from collections import defaultdict, deque
from fastapi import Header, HTTPException, Request, status
from app.config import get_settings

async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not hmac.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

class InMemoryRateLimiter:
    """Single-process demo limiter; use Redis or an API gateway for multiple workers."""
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
    def check(self, request: Request) -> None:
        cfg = get_settings()
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[key]
        while hits and hits[0] <= now - cfg.rate_limit_window_seconds:
            hits.popleft()
        if len(hits) >= cfg.rate_limit_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        hits.append(now)
