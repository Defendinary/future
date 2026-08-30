from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class CORSMiddleware(IMiddleware):
    name = "CORSMiddleware"
    allow_origin = "*"
    allow_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    allow_headers = "origin, content-type, accept, authorization, x-xsrf-token, x-request-id"
    allow_credentials = "false"

    def _apply_headers(self) -> None:
        self.response.headers.append([b"access-control-allow-origin", self.allow_origin.encode("utf-8")])
        self.response.headers.append([b"access-control-allow-methods", self.allow_methods.encode("utf-8")])
        self.response.headers.append([b"access-control-allow-headers", self.allow_headers.encode("utf-8")])
        if self.allow_origin != "*":
            self.response.headers.append([b"access-control-allow-credentials", self.allow_credentials.encode("utf-8")])

    async def before(self) -> Optional[Response]:
        if self.request.method == "OPTIONS":
            self.response.empty(status=204)
            self._apply_headers()
            return self.response
        return None

    async def after(self) -> Optional[Response]:
        self._apply_headers()
        return None
