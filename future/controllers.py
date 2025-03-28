from future.request import Request
from future.response import Response, JSONResponse
#from future.graphql import GraphQL
import json
from textwrap import dedent


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

"""
✅ Why defining class methods without self is valid in Python:
self is a naming convention, not a keyword — Python doesn't require it.

Functions defined in a class become methods only when called via an instance.

If you call them on the class (ClassName.method()), no self is passed — so it's valid to omit it.

The code is valid Python and works without error as long as you don't instantiate the class.

Linters like Pylance assume all methods are instance methods unless decorated — but this is just a warning, not a Python error.

Python allows any name or no parameter at all; def method(): ... inside a class is legal and callable from the class.

Adding self when it's unused is misleading and violates clarity — it implies instance state is accessed when it's not.

Metaclasses or conventions can be used to treat methods as static implicitly — decorators are not required for static behavior.

This pattern is commonly used in frameworks (e.g., FastAPI) where function-style handlers live in classes but are not instance-bound.
"""

class Controller:
    # __new__ is inherited automatically so we do not have to super.__init__() classes that extend it 
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} may not be instantiated. This is a hack to prevent mistakes and helps us keep controller methods static.")

"""
class GraphQLController(Controller):
    graphql = GraphQL()

    async def query(request: Request) -> Response:
        query = dedent('''
            query GetEverything {
                users {
                    id
                    name
                    email
                }
                posts {
                    id
                    title
                    content
                    author {
                    name
                    }
                }
            }
        ''')    
        #query = {"query": query}
        result = await GraphQLController.graphql.execute(query)
        return Response(body=json.dumps(result).encode())
"""

class DebugController(Controller):
    async def test(request: Request):  # type: ignore[no-self]
        return Response(body=b"lolok\n")

    async def test_data(request: Request, data) -> Response:  # type: ignore[no-self]
        return Response(body=f"data: {data}".encode(), status=200)

    async def some_handler(request: Request, **params) -> Response:  # type: ignore[no-self]
        return Response(body=f"Handled with params: {params}".encode(), status=200)


class ORMController(Controller):
    async def test(request: Request):  # type: ignore[no-self]
        r = {
            "message": "hi",
        }
        return JSONResponse(body=json.dumps(r).encode())  # FIXME: ... json response





class WelcomeController(Controller):
    async def root(request: Request) -> Response:  # type: ignore[no-self]
        # return Response(body="✨ Welcome to Future! ✨")
        return Response(body=b"Welcome to Future!\n")

    async def ping(request: Request) -> Response:  # type: ignore[no-self]
        return Response(body=b"Pong\n")

    async def test(request: Request, data) -> Response:  # type: ignore[no-self]
        return Response(body=data, status=200)

    async def args(request: Request, user_id, arg2) -> Response:  # type: ignore[no-self]
        return Response(body=f"{user_id=}, {arg2=}\n".encode())

    async def openapi(request: Request) -> Response:  # type: ignore[no-self]
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
