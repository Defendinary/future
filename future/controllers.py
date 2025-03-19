from future.request import Request
from future.response import Response, JSONResponse
import json

"""
\"""
Example API implemented using a controller.
\"""
from typing import List, Optional
from blacksheep.server.controllers import Controller, get, post

class ExamplesController(Controller):
    @classmethod
    def route(cls) -> Optional[str]:
        return "/api/examples"

    @classmethod
    def class_name(cls) -> str:
        return "Examples"

    @get()
    async def get_examples(self) -> List[str]:
        \"""
        Gets a list of examples.
        \"""
        return list(f"example {i}" for i in range(3))

    @post()
    async def add_example(self, example: str):
        \"""
        Adds an example.
        \"""

"""

class Controller:
    pass


class DebugController:
    async def test(request: Request, data) -> Response:  # type: ignore[reportSelfClsParameterName]
        return Response(body=f"data: {data}".encode(), status=200)

    async def some_handler(request: Request, **params) -> Response:  # type: ignore[reportSelfClsParameterName]
        return Response(body=f"Handled with params: {params}".encode(), status=200)


class ORMController:
    async def test(request: Request):  # type: ignore[reportSelfClsParameterName]
        r = {
            "message": "hi",
        }
        return JSONResponse(body=json.dumps(r).encode())  # FIXME: ... json response


class WelcomeController(Controller):
    async def root(request: Request) -> Response:  # type: ignore[reportSelfClsParameterName]
        # return Response(body="✨ Welcome to Future! ✨")
        return Response(body=b"Welcome to Future!\n")

    async def ping(request: Request) -> Response:  # type: ignore[reportSelfClsParameterName]
        return Response(body=b"Pong\n")

    async def test(request: Request, data) -> Response:  # type: ignore[reportSelfClsParameterName]
        return Response(body=data, status=200)

    async def args(request: Request, user_id, arg2) -> Response:  # type: ignore[reportSelfClsParameterName]
        return Response(body=f"{user_id=}, {arg2=}\n".encode())

    async def openapi(request: Request) -> Response:  # type: ignore[reportSelfClsParameterName]
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Simple ASGI App",
                "version": "1.0.0",
            },
            "paths": {},
        }
        return Response(
            body=json.dumps(openapi_schema).encode("utf-8"),
            headers=[[b"content-type", b"application/json"]],
            status=200,
        )
