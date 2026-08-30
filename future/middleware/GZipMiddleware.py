from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class GZipMiddleware(IMiddleware):
    name = "GZipMiddleware"

    async def after(self) -> Optional[Response]:
        accept = self.request.headers.get("accept-encoding", "")
        if "gzip" not in accept.lower():
            return None
        if not self.response.body:
            return None
        for key, _value in self.response.headers:
            if key.lower() == b"content-encoding":
                return None
        import gzip
        compressed = gzip.compress(self.response.body)
        self.response.body = compressed
        self.response.headers = [pair for pair in self.response.headers if pair[0].lower() != b"content-length"]
        self.response.headers.append([b"content-encoding", b"gzip"])
        self.response.headers.append([b"content-length", str(len(compressed)).encode("utf-8")])
        return None
