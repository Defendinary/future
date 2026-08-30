from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class TestMiddlewareResponse(IMiddleware):
    name = "testResponseMiddleware"

    async def after(self) -> Optional[Response]:
        if self.request.headers.get("x-interrupt-response") == "1":
            return self.response.text("Response intercepted!")
        return None
