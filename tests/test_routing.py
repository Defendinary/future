import pytest
import asyncio
from future.application import Future, Lifespan
from future.routing import RouteGroup, Get
from future.controllers import WelcomeController
from future.testclient import FutureTestClient



async def test_route_single_without_domain():
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    app = Future(lifespan=Lifespan, debug=False)
    app.add_routes(routes=routes)
    
    # You should use `FutureTestClient` as a context manager, to ensure that the lifespan is called.
    async with FutureTestClient(app) as client:
        # Application's lifespan is called on entering the block.
        response = await client.get("http://127.0.0.1/")
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"
    # And the lifespan's teardown is run when exiting the block.
    

async def test_route_single_with_domain():
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    app = Future(lifespan=Lifespan, debug=False, domain="example.com")
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"


async def test_route_group() -> None:
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ]
        ),
    ]

    app = Future(lifespan=Lifespan, debug=False, domain="example.com")
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "api.example.com"})
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"


  
async def test_single_route_with_domain():
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    app = Future(lifespan=Lifespan, debug=False, domain="example.com")
    app.add_routes(routes=routes)
    
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"



async def test_domain_routing() -> None:
    routes = [
        RouteGroup(
            name="test",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ]
        ),
    ]

    app = Future(lifespan=Lifespan, debug=False, domain="example.com")
    app.add_routes(routes=routes)
    
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"
    

