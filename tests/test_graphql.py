from future.application import Future, Lifespan
from future.routing import RouteGroup, Get
from future.testclient import FutureTestClient



async def test_graphql():
    
    
    
    
    
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Get(path="/userposts", methods=["GET"], endpoint=get_user_posts, name="GetUserPosts")  # type: ignore[reportAttributeAccessIssue]
            ]
        ),
    ]

    app = Future(lifespan=Lifespan, debug=False, domain="example.com")
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "api.example.com"})
        assert response.status_code == 200
        assert response.text == "Welcome to Future!\n"
