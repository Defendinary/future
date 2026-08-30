from future.interfaces.IController import IController
from future.response import Response


class WelcomeController(IController):
    async def root(self) -> Response:
        return self.response.text("✨ Welcome to Future! ✨")
