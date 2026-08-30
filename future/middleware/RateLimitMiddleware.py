from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class RateLimitMiddleware(IMiddleware):
    name = "RateLimitMiddleware"
    limit = 60
    window_seconds = 60
    _hits: dict[str, list[float]] = {}

    async def before(self) -> Optional[Response]:
        import time
        client = (self.request.scope.get("client") or ("unknown", 0))[0]
        now = time.time()
        bucket = self._hits.setdefault(client, [])
        cutoff = now - self.window_seconds
        self._hits[client] = [stamp for stamp in bucket if stamp >= cutoff]
        if len(self._hits[client]) >= self.limit:
            return self.response.json({"error": "Too Many Requests", "status_code": 429}, status=429)
        self._hits[client].append(now)
        return None
