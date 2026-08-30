from future.application import Future
from future.interfaces.IController import IController
from future.database import Database
from future.databases.SQLiteDatabase import SQLiteDatabase
from future.middleware.CORSMiddleware import CORSMiddleware
from future.middleware.GZipMiddleware import GZipMiddleware
from future.middleware.ScopeValidationMiddleware import ScopeValidationMiddleware
from future.middleware.SessionMiddleware import SessionMiddleware
from future.middleware.SessionMiddleware import SESSION_COOKIE_NAME
from future.interfaces.IMiddleware import IMiddleware
from future.interfaces.IModel import IModel
from future.openapi import rebuild_spec_from_routes
from future.response import Response
from future.routing import Get, RouteGroup
from future.lifespan import Lifespan
from future.testclient import FutureTestClient


class BadController(IController):
    async def index(self):
        return {"ok": True}


class GoodController(IController):
    async def index(self) -> Response:
        return self.response.json({"ok": True})


class GrantScopes(IMiddleware):
    async def before(self):
        header = self.request.headers.get("x-scopes")
        if header:
            self.request.context["user_id"] = "u1"
            self.request.context["scopes"] = [part for part in header.split(",") if part]
        return None


class SessionController(IController):
    async def login(self) -> Response:
        self.request.session["user"] = "alice"
        return self.response.json({"ok": True})

    async def logout(self) -> Response:
        self.request.session.clear()
        return self.response.json({"ok": True})


class Item(IModel):
    __connection__ = "default"
    __table__ = "gap_items"
    id: str
    name: str


def _base_config(**extra):
    config = {"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "OPENAPI": {"enabled": True, "auto_routes": False}}
    config.update(extra)
    return config


async def test_controller_must_return_response():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Main", routes=[Get("/bad", BadController.index, "bad")])])
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/bad")
        assert response.status_code == 500


async def test_controller_json_response_ok():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Main", routes=[Get("/ok", GoodController.index, "ok")])])
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/ok")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


def test_set_cookie_max_age_and_domain():
    response = Response()
    response.set_cookie("a", "b", max_age=3600, domain="example.com", expires="Thu, 01 Jan 1970 00:00:00 GMT")
    cookie = response.headers[-1][1].decode("utf-8")
    assert "Max-Age=3600" in cookie
    assert "Domain=example.com" in cookie
    assert "Expires=" in cookie


async def test_session_clear_deletes_cookie():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([
        RouteGroup(
            name="Auth",
            middlewares=[SessionMiddleware],
            routes=[
                Get("/login", SessionController.login, "login"),
                Get("/logout", SessionController.logout, "logout"),
            ],
        ),
    ])
    async with FutureTestClient(app) as client:
        login = await client.get("http://127.0.0.1/login")
        assert login.status_code == 200
        set_cookies = [h for h in login.headers.get_list("set-cookie") if SESSION_COOKIE_NAME in h]
        assert set_cookies
        logout = await client.get("http://127.0.0.1/logout", headers={"cookie": set_cookies[0].split(";", 1)[0]})
        assert logout.status_code == 200
        clear_cookies = [h for h in logout.headers.get_list("set-cookie") if SESSION_COOKIE_NAME in h]
        assert clear_cookies
        assert "Max-Age=0" in clear_cookies[0]


def test_openapi_tags_from_routegroup_name():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Trades", routes=[Get("/trades", GoodController.index, "trades")])])
    spec = rebuild_spec_from_routes(app.routes, app.config)
    assert spec["paths"]["/trades"]["get"]["tags"] == ["Trades"]


async def test_cors_options_and_get():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Main", middlewares=[CORSMiddleware], routes=[Get("/x", GoodController.index, "x")])])
    async with FutureTestClient(app) as client:
        options = await client.client.request("OPTIONS", "http://127.0.0.1/x")
        assert options.status_code == 204
        assert options.headers.get("access-control-allow-origin") == "*"
        get = await client.get("http://127.0.0.1/x")
        assert get.status_code == 200
        assert get.headers.get("access-control-allow-origin") == "*"


async def test_gzip_middleware():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Main", middlewares=[GZipMiddleware], routes=[Get("/x", GoodController.index, "x")])])
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/x", headers={"accept-encoding": "gzip"})
        assert response.status_code == 200
        assert response.headers.get("content-encoding") == "gzip"
        assert response.json() == {"ok": True}


async def test_future_registers_databases_from_config():
    Database._connections = {}
    Database._default = None
    databases = {"default": "sqlite", "sqlite": SQLiteDatabase(database=":memory:")}
    app = Future(lifespan=Lifespan(), config=_base_config(DATABASES=databases))
    assert app.databases is databases
    connection = Database().get_connection("default")
    from future.migrations import Blueprint
    blueprint = Blueprint("gap_items", "default", action="create")
    blueprint.id()
    blueprint.string("name")
    await connection.schema_create(blueprint)
    await Item(id="1", name="wired").save()
    found = await Item.find("1")
    assert found is not None
    assert found.name == "wired"


async def test_scope_validation_uses_context_scopes():
    app = Future(lifespan=Lifespan(), config=_base_config())
    app.add_routes([RouteGroup(name="Main", middlewares=[GrantScopes, ScopeValidationMiddleware], routes=[Get("/x", GoodController.index, "x", scopes=["read:api"])])])
    async with FutureTestClient(app) as client:
        missing_user = await client.get("http://127.0.0.1/x")
        assert missing_user.status_code == 401
        denied = await client.get("http://127.0.0.1/x", headers={"x-scopes": "write:api"})
        assert denied.status_code == 403
        allowed = await client.get("http://127.0.0.1/x", headers={"x-scopes": "read:api"})
        assert allowed.status_code == 200
        assert allowed.json() == {"ok": True}
