from typing import Any

from future.interfaces.IController import IController
from future.response import WebSocketResponse


class WebSocketController(IController):
    """Controller for WebSocket endpoints."""

    async def websocket_handler(self, **params: Any) -> WebSocketResponse:
        """Echo WebSocket: greeting, then duplex Echo: <text> until disconnect."""
        message = params.get("message", "Hello from WebSocket!")
        return WebSocketResponse(self.request.receive, message=message)
