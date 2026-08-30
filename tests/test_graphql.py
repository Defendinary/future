from future.application import Future
from future.controllers.GraphQLController import GraphQLController
from future.database import Database
from future.databases.SQLiteDatabase import SQLiteDatabase
from future.lifespan import Lifespan
from future.migrations import Blueprint
from future.models.PostModel import PostModel
from future.models.UserModel import UserModel
from future.routing import Post, RouteGroup
from future.testclient import FutureTestClient


async def _app():
    databases = {
        "default": "sqlite",
        "sqlite": SQLiteDatabase(database=":memory:"),
    }
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Post(path="/graphql", endpoint=GraphQLController.query, name="GraphQL")  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]
    app = Future(lifespan=Lifespan(), config={"APP_DOMAIN": "example.com", "DATABASES": databases})
    app.add_routes(routes=routes)
    users = Blueprint("users", "default", action="create")
    users.id()
    users.string("name")
    users.string("email")
    await Database().get_connection("default").schema_create(users)
    posts = Blueprint("posts", "default", action="create")
    posts.id()
    posts.string("title")
    posts.string("content")
    posts.string("author_id")
    await Database().get_connection("default").schema_create(posts)
    await UserModel(id="1", name="Alice", email="alice@example.com").save()
    await UserModel(id="2", name="Bob", email="bob@example.com").save()
    await PostModel(id="101", title="GraphQL vs REST", content="GraphQL is amazing!", author_id="1").save()
    await PostModel(id="102", title="Strawberry Rocks", content="Strawberry is great for Python!", author_id="2").save()
    return app


async def test_graphql() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        response = await client.post(
            "http://127.0.0.1/graphql",
            headers={"Host": "api.example.com"},
            json={"email": "alice@example.com", "name": "Alice", "title": "Strawberry Rocks"},
        )
        assert response.status_code == 200
        body = response.json()
        users = body["data"]["users"]
        posts = body["data"]["posts"]
        assert {user["email"] for user in users} == {"alice@example.com"}
        assert len(posts) == 1
        assert posts[0]["title"] == "Strawberry Rocks"
        assert posts[0]["author"]["name"] == "Bob"


async def test_graphql_terms_are_separate_searches() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        response = await client.post(
            "http://127.0.0.1/graphql",
            headers={"Host": "api.example.com"},
            json={"name": "Alice", "email": "bob@example.com"},
        )
        assert response.status_code == 200
        emails = {user["email"] for user in response.json()["data"]["users"]}
        assert emails == {"alice@example.com", "bob@example.com"}


async def test_graphql_missing_query() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        response = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json={})
        assert response.status_code == 400
        assert "errors" in response.json()


async def test_graphql_by_id_and_author_id() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        by_id = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json={"id": "1"})
        assert by_id.status_code == 200
        assert {user["name"] for user in by_id.json()["data"]["users"]} == {"Alice"}
        by_author = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json={"author_id": "1"})
        assert by_author.status_code == 200
        posts = by_author.json()["data"]["posts"]
        assert len(posts) == 1
        assert posts[0]["title"] == "GraphQL vs REST"
        assert posts[0]["author"]["name"] == "Alice"


async def test_graphql_rejects_non_object_json() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        response = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json=["email"])
        assert response.status_code == 400
        assert "errors" in response.json()


async def test_graphql_rejects_bad_limit() -> None:
    app = await _app()
    async with FutureTestClient(app) as client:
        response = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json={"name": "Alice", "limit": "nope"})
        assert response.status_code == 400
        assert "limit" in response.json()["errors"][0]
