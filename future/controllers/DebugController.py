from typing import Any

from future.interfaces.IController import IController
from future.response import Response


class DebugController(IController):
    async def test(self) -> Response:
        return self.response.text("lolok")

    async def hello(self) -> Response:
        return self.response.json({"message": "hi"})

    async def test_data(self, data: Any) -> Response:
        return self.response.text(f"data: {data}", status=200)

    async def some_handler(self, **params: Any) -> Response:
        return self.response.text(f"Handled with params: {params}", status=200)

    async def ping(self) -> Response:
        return self.response.text("Pong\n")

    async def test2(self, data: Any) -> Response:
        return self.response.text(str(data), status=200)

    async def args(self, user_id: Any, arg2: Any) -> Response:
        return self.response.text(f"{user_id=}, {arg2=}\n")
