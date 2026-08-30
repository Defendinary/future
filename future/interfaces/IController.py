from future.interfacing import Interface
from future.request import Request
from future.response import Response


class IController(Interface):
    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response
