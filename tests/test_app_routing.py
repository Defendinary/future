import pytest
import asyncio
from future.application import Future, Lifespan
from future.routing import RouteGroup, Get
from future.controllers import WelcomeController
from future.testclient import FutureTestClient


async def test_application() -> None:
    routes = [
        RouteGroup(
            name="test_application_routes",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
            ]
        ),
    ]

    app = Future(lifespan=Lifespan, name="test_application", debug=False, domain="example.com")
    app.add_routes(routes=routes)

    # You should use `FutureTestClient` as a context manager, to ensure that the lifespan is called.
    async with FutureTestClient(app) as client:
        # Application's lifespan is called on entering the block.
        response = await client.get("http://example.com/")
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"
    # And the lifespan's teardown is run when exiting the block.



from future.application import Future, Lifespan
from future.controllers import WelcomeController
from future.middleware import ResponseCodeConfuser, TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import RouteGroup, Get
from enum import Enum


app = Future(lifespan=Lifespan, name="Future", debug=True, domain="example.com")

routes = [
    Get(path='/ping', endpoint=WelcomeController.ping, name="Ping", middlewares=[TestMiddlewareRequest]),
    
    RouteGroup(
        name="test",
        subdomain="api",
        prefix="/api",
        middlewares=[
            #ResponseCodeConfuser,
        ],
        routes=[
            Get(path='/', endpoint=WelcomeController.root, name="welcome"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path='/users/<int:user_id>/<str:arg2>', endpoint=WelcomeController.args, name="getUserInfo"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/cats/<int:cat_id>", endpoint=some_handler, name="get_cat"),  # type: ignore[reportAttributeAccessIssue]
            #Get(path="/api/dogs/<uuid:dog_id>", endpoint=some_handler, name="get_dog"),  # type: ignore[reportAttributeAccessIssue]
        ],
    ),
]

app.add_routes(routes=routes)
print(app.routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, workers=1)



