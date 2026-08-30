from typing import Optional

from future.interfacing import Interface
from future.request import Request
from future.response import Response


# README - a note on the use of middlewares:
# if a middleware does not RETURN or hit any EXCEPTIONS, it means it passes (all checks ok)
# if it however RETURNS or hits an EXCEPTION, the middleware check will deny further processing of the request.


class IMiddleware(Interface):
    name: Optional[str] = None
    apply: bool = True
    priority: int = 0

    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response

    async def before(self) -> Optional[Response]:
        return None

    async def after(self) -> Optional[Response]:
        return None
