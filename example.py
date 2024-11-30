#!/usr/bin/env python3
"""
Runs the application for local development. This file should not be used to start the
application for production.

Refer to https://www.uvicorn.org/deployment/ for production deployments.
"""

from future.application import Future
from future.controller import WelcomeController
from future.middleware import ResponseCodeConfuser, TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import RouteGroup, Get
import os


from future.logger import setup_logging
from future.request import Request
from future.response import Response
from future.middleware import Middleware
from future.controller import WelcomeController
from future.routing import *
from future.types import ASGIScope, ASGIReceive, ASGISend
from typing import Any, Callable, Optional, Union, TypedDict
from rich.console import Console
import re
import logging
import uvicorn

setup_logging()


# spawn background tasks in the lifespan startup process... or database connections etc...
# on shutdown, save shit, send info about shutdown etc...
from pprint import pprint as print

#@dataclass
class Lifespan:
    #app: ASGIApp
    
    async def __aenter__(self):
        print("startup things")
    
    async def __aexit__(self, exc_type, exc_value, tb) -> bool | None:
        print("shutdown things")
        None

async def lifespan(app):
    async with asyncio.timeout(30):
        print("startup things")
        #await.could_hang_forever()
    try:
        yield # { "a": "b" } # yields stuff into scope
    finally:
        async with asyncio.timeout(30):
            print("shutdown things")


class Future:
    def __init__(self, lifespan, name: str = "Future", debug: bool = False, domain: str = ""):
        self.lifespan = lifespan
        self.debug = debug
        self.domain = domain
        self.logger = logging.getLogger(name)
        self.routes: dict[str, list[EndpointConfig]] = {}

    def _add_route(self, route: Route, subdomain: Optional[str] = None) -> None:
        if subdomain not in self.routes:
            self.routes[subdomain] = []

        before = []
        after = []
        for middleware in route.middlewares:
            if middleware.attach_to == "request":
                before.append(middleware)
            elif middleware.attach_to == "response":
                after.append(middleware)

        before.sort(key=lambda middleware: middleware.priority)
        after.sort(key=lambda middleware: middleware.priority)

        endpoint_config = EndpointConfig(
            #endpoint=route.endpoint,
            middleware_before=before,
            middleware_after=after,
            #regex={"paths": [route._rx]},
            #og_path=route.path,
            route=route  # Include the full Route object
        )

        self.routes[subdomain].append(endpoint_config)

    def add_routes(self, routes: list[Union[Route, RouteGroup]]) -> None:
        for x in routes:
            if isinstance(x, Route):
                self._add_route(
                    route=x,
                    subdomain=None
                )

            elif isinstance(x, RouteGroup):
                for route in x.routes:
                    full_path = f"{x.prefix}{route.path}"
                    combined_middlewares = x.middlewares + route.middlewares
                    route.path = full_path
                    route.middlewares = combined_middlewares
                    self._add_route(
                        route=route,
                        subdomain=x.subdomain
                    )
            else:
                raise NotImplementedError

    async def handle_lifespan(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        assert scope["type"] == "lifespan"
        message = await receive()
        assert message["type"] == "lifespan.startup"
        started = False
        app = scope.get("app")
        try:
            async with self.lifespan(app) as state:
                if state is not None:
                    scope["state"].update(state)
                await send({"type": "lifespan.startup.complete"})
                started = True
                message = await receive()
                assert message["type"] == "lifespan.shutdown"
        except BaseException:
            event_type = "lifespan.shutdown.failed" if started else "lifespan.startup.failed"
            await send({"type": event_type, "message": traceback.format_exc()})
            raise
        await send({"type": "lifespan.shutdown.complete"})


    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        # Inject ourselves into the chain for later convenience
        scope["app"] = self
        print(scope)
        
        if scope["type"] == "lifespan":
            await self.handle_lifespan(scope, receive, send)
        
        
        
        
        request = Request(scope, receive)

        host_header_parts = request.host.split(".") if request.host else []
        subdomain = host_header_parts[0] if len(host_header_parts) > 2 else ""
        domain = (
            host_header_parts[-2] + "." + host_header_parts[-1]
            if len(host_header_parts) > 1
            else ""
        )

        if domain != self.domain and not self.debug:
            response = Response(body=b"Not Found", status=404)
            await response(send)
            return

        request_path = request.path.encode()
        subdomain_routes = self.routes.get(subdomain, [])
        matched_route = None
        route_params = None

        # Perform the actual regex matching
        for epc in subdomain_routes:
            route: Route = epc["route"]
            route_match: RouteMatch = route.match(request_path)
            if route_match:
                matched_route = epc
                route_params = route_match.params
                break

        if matched_route is None:
            response = Response(body=b"Not Found", status=404)
            await response(send)
            return

        # See if we can unfuck anything here:
        #endpoint = subdomain_routes.get(request_path).get('endpoint', None)
        middleware_before = matched_route["middleware_before"]
        middleware_after = matched_route["middleware_after"]
        endpoint = matched_route["route"].endpoint

        for b_middleware in middleware_before:
            response = b_middleware.intercept(request)
            if response is not None:
                await response(send)
                return
        
        if route_params:
            response = await endpoint(request, **route_params)
        else:
            response = await endpoint(request)

        for a_middleware in middleware_after:
            modified_response = a_middleware.intercept(request, response)
            if modified_response is not None:
                response = modified_response

        await response(send)


    def run(self, host: str = "127.0.0.1", port: int = 8000, workers: int = 4, tls_key: Optional[str] = None, tls_cert: Optional[str] = None, tls_password: Optional[str] = None) -> None:
        console = Console()
        console.rule("[bold yellow]Running for local development", align="left")
        console.print(f"[bold yellow]Visit http://localhost:{port}/docs")
        uvicorn.run(
            app="__main__:app",
            host=host,
            port=port,
            workers=workers,
            reload=self.debug,
            ssl_keyfile=tls_key,
            ssl_certfile=tls_cert,
            ssl_keyfile_password=tls_password,
            timeout_graceful_shutdown=3,
            log_level="info",
        )



# Example usage
async def aString(request: Request, arg1) -> Response:
    return Response(body=f"{arg1=}".encode())

async def anInt(request: Request, arg1, arg2) -> Response:
    return Response(body=f"{arg1=}, {arg2=}".encode())



app = Future(lifespan=Lifespan(), name="Future", debug=False, domain="example.com:8000")

routes = [
    # Grouped routes
    RouteGroup(
        name="test",
        subdomain="api",
        middlewares=[
            #TestMiddlewareRequest,
            #TestMiddlewareResponse,
            #ResponseCodeConfuser,
        ],
        routes=[
            Get(path='/', endpoint=WelcomeController.root, name="Welcome"),
            Get(path='/example/<str:aString>', endpoint=aString, name="aString"),
            Get(path='/example/<int:one>/<str:two>', endpoint=anInt, name="anInt"),
        ],
    ),

    # Also test Single Routes
    Get(path='/ping', endpoint=WelcomeController.ping, name="Ping", middlewares=[TestMiddlewareRequest]),
]

app.add_routes(routes)
#print(app.routes)

if __name__ == "__main__":
    #os.environ["APP_ENV"] = "dev"
    #port = int(os.environ.get("APP_PORT", 44777))
    app.run(host="0.0.0.0", port=8000, workers=1)
