from typing import Callable, Optional, Union, Any, Dict, List
from common import Request, Response, ASGIScope, ASGIReceive, ASGISend
import uvicorn

class WebSocketEndpointConfig:
    def __init__(
        self,
        endpoint: Callable,
        regex: dict,
        og_path: str,
        route: 'Route'
    ):
        self.endpoint = endpoint
        self.regex = regex
        self.og_path = og_path
        self.route = route


class Future:
    def __init__(self, name: str = "Future", debug: bool = False, domain: str = ""):
        self.debug = debug
        self.domain = domain
        self.logger = logging.getLogger(name)
        self.routes: dict[str, list[EndpointConfig]] = {}
        self.websocket_routes: dict[str, list[WebSocketEndpointConfig]] = {}

    def _add_route(self, route: Route, subdomain: Optional[str] = None) -> None:
        if route.methods == ["WEBSOCKET"]:
            if subdomain not in self.websocket_routes:
                self.websocket_routes[subdomain] = []
            config = WebSocketEndpointConfig(
                endpoint=route.endpoint,
                regex={"paths": [route._rx]},
                og_path=route.path,
                route=route,
            )
            self.websocket_routes[subdomain].append(config)
        else:
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

            config = EndpointConfig(
                endpoint=route.endpoint,
                middleware_before=before,
                middleware_after=after,
                regex={"paths": [route._rx]},
                og_path=route.path,
                route=route,
            )
            self.routes[subdomain].append(config)

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

    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        request_type = scope["type"]

        if request_type == "websocket":
            await self.handle_websocket(scope, receive, send)
        elif request_type == "http":
            await self.handle_http(scope, receive, send)
        else:
            response = Response(body=b"Unsupported protocol", status=500)
            await response(send)

    async def handle_http(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
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

        for route_config in subdomain_routes:
            route = route_config.route
            route_match = route.match(request_path)
            if route_match:
                matched_route = route_config
                route_params = route_match.params
                break

        if matched_route is None:
            response = Response(body=b"Not Found", status=404)
            await response(send)
            return

        endpoint = matched_route.endpoint
        middleware_before = matched_route.middleware_before
        middleware_after = matched_route.middleware_after

        for b_middleware in middleware_before:
            response = b_middleware.intercept(request)
            if response is not None:
                await response(send)
                return

        response = await endpoint(request, **route_params)

        for a_middleware in middleware_after:
            modified_response = a_middleware.intercept(request, response)
            if modified_response is not None:
                response = modified_response

        await response(send)

    async def handle_websocket(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        path = scope["path"].encode()
        subdomain = scope.get("headers", {}).get(b"host", b"").decode().split(".")[0] if "headers" in scope else ""
        subdomain_routes = self.websocket_routes.get(subdomain, [])
        matched_route = None
        route_params = None

        for route_config in subdomain_routes:
            route = route_config.route
            route_match = route.match(path)
            if route_match:
                matched_route = route_config
                route_params = route_match.params
                break

        if matched_route is None:
            await send({"type": "websocket.close", "code": 404})
            return

        endpoint = matched_route.endpoint

        try:
            await endpoint(scope, receive, send, **route_params)
        except Exception as ex:
            self.logger.exception("Exception in WebSocket endpoint: %s", ex)
            await send({"type": "websocket.close", "code": 1011})

    def run(self, host: str = "127.0.0.1", port: int = 8000, workers: int = 4, tls_key: Optional[str] = None, tls_cert: Optional[str] = None, tls_password: Optional[str] = None) -> None:
        uvicorn.run(
            app="__main__:app",
            host=host,
            port=port,
            workers=workers,
            reload=self.debug,
            ssl_keyfile=tls_key,
            ssl_certfile=tls_cert,
            ssl_keyfile_password=tls_password,
        )


# Example WebSocket Usage
async def websocket_handler(scope: ASGIScope, receive: ASGIReceive, send: ASGISend, **params: Any) -> None:
    await send({"type": "websocket.accept"})
    while True:
        message = await receive()
        if message["type"] == "websocket.receive":
            await send({"type": "websocket.send", "text": f"Echo: {message['text']}"})
        elif message["type"] == "websocket.disconnect":
            break

app = Future(name="FutureApp", debug=True, domain="example.com")

routes = [
    RouteGroup(
        name="websockets",
        subdomain="api",
        routes=[
            Route(
                methods=["WEBSOCKET"],
                path="/ws/<int:id>",
                endpoint=websocket_handler,
                name="websocket_endpoint",
            ),
        ],
    ),
]

app.add_routes(routes)

if __name__ == "__main__":
    app.run()
