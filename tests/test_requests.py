from future.application import Future
from future.lifespan import Lifespan
from future.routing import Post
from future.testclient import FutureTestClient


async def test_post_json_data() -> None:
    """Test POST request with JSON data."""
    from future.request import Request
    from future.response import Response
    
    async def post_handler(request: Request, response: Response) -> Response:
        json_data = await request.json()
        return Response(body=f"Received: {json_data}", status=200)

    routes = [
        Post(path="/post", endpoint=post_handler, name="POST Handler"),
    ]

    config = {
        "APP_NAME": "test_post",
        "APP_DOMAIN": "",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        url = "http://127.0.0.1/post"
        json_data = {
            "message": "Hello POST",
            "number": 42,
        }
        headers={
            "Content-Type": "application/json"
        }
        response = await client.post(url=url, json=json_data, headers=headers)
        assert response.status_code == 200
        assert "Hello POST" in response.text

async def test_post_form_data() -> None:
    """Test POST request with form data."""
    from future.request import Request
    from future.response import Response
    
    async def form_handler(request: Request, response: Response) -> Response:
        form_data = await request.form()
        return Response(body=f"Received form: {form_data}", status=200)
    
    routes = [
        Post(path="/form", endpoint=form_handler, name="Form Handler"),
    ]
    
    config = {
        "APP_NAME": "test_post_form",
        "APP_DOMAIN": "",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        url = "http://127.0.0.1/form"
        form_data = "message=Hello+form&number=42&blank="
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = await client.post(url, data=form_data, headers=headers)
        assert response.status_code == 200
        assert "Hello form" in response.text
        assert "42" in response.text
        assert "'blank': ''" in response.text


async def test_query_string_and_cookies() -> None:
    from future.request import Request
    from future.response import Response
    from future.routing import Get

    async def handler(request: Request, response: Response) -> Response:
        return response.json({"q": request.query.get("q"), "tags": request.query.get("tag"), "sid": request.cookies.get("sid")})

    app = Future(lifespan=Lifespan(), config={"APP_NAME": "test_query", "APP_DOMAIN": "", "APP_DEBUG": False})
    app.add_routes([Get(path="/search", endpoint=handler, name="Search")])
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/search?q=hello&tag=a&tag=b", headers={"cookie": "sid=abc"})
        assert response.status_code == 200
        body = response.json()
        assert body["q"] == "hello"
        assert body["tags"] == ["a", "b"]
        assert body["sid"] == "abc"
