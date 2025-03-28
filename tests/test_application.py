import pytest
import asyncio
from future.application import Future, Lifespan
from future.routing import RouteGroup, Get
from future.controllers import WelcomeController
from future.testclient import FutureTestClient


async def test_application_subdomains() -> None:
    routes = [
        RouteGroup(
            name="test_application_routes",
            subdomain="api",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ]
        ),
    ]

    app = Future(lifespan=Lifespan, name="test_application_subdomains", debug=False, domain="example.com")
    app.add_routes(routes=routes)
    
    # Ensure debug is disabled since subdomain routing is not supported in debug mode.
    assert app.debug == False

    async with FutureTestClient(app) as client:
        response = await client.get("http://api.example.com/")
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"
