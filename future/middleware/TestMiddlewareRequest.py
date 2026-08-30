from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class TestMiddlewareRequest(IMiddleware):
    name = "testRequestMiddleware"

    async def before(self) -> Optional[Response]:
        if self.request.headers.get("x-interrupt") == "1":
            return self.response.text("Request intercepted!")
        return None
