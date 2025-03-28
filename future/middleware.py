from future.request import Request
from future.response import Response
import random

# CSRF: https://github.com/simonw/asgi-csrf
# CSP: Content Security Policy


# README - a note on the use of middlewares:
# if a middleware does not RETURN or hit any EXCEPTIONS, it means it passes (all checks ok)
# if it however RETURNS or hits an EXCEPTION, the middleware check will deny further processing of the request.

class Middleware:
    name = None
    apply = True
    priority = 0
    attach_to = "request"

    def intercept(request: Request) -> Response:  # type: ignore[reportAttributeAccessIssue]
        # return Response(b"Intercepted!")
        ...

class TestMiddlewareRequest(Middleware):
    name = "testReq"
    attach_to = "request"

    def intercept(request: Request) -> Response:  # type: ignore[reportAttributeAccessIssue]
        return Response(body=b"req")

class TestMiddlewareResponse(Middleware):
    name = "testResp"
    attach_to = "response"

    def intercept(request: Request, response: Response) -> Response:  # type: ignore[reportAttributeAccessIssue]
        return Response(body=b"resp")


# ----


class ResponseCodeConfuser(Middleware):
    name = "response code confuser"
    attach_to = "response"

    def intercept(request: Request, response: Response) -> Response:  # type: ignore[reportAttributeAccessIssue]
        response_codes = [
            100,
            101,
            102,
            103,
            200,
            201,
            202,
            203,
            204,
            205,
            206,
            207,
            208,
            226,
            300,
            301,
            302,
            303,
            304,
            305,
            306,
            307,
            308,
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            407,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            417,
            418,
            421,
            422,
            423,
            424,
            425,
            426,
            428,
            429,
            431,
            451,
            500,
            501,
            502,
            503,
            504,
            505,
            506,
            507,
            508,
            510,
            511,
        ]

        # fuck with people using cURL to test
        if "curl" in request.headers["user-agent"]:
            random_code = random.choice(response_codes)
            # return EmptyResponse(status=random_code)
            return Response(status=random_code)


class RateLimitMiddleware(Middleware):
    pass


class CSRFMiddleware(Middleware):
    pass


class WebServerConfuser(Middleware):
    pass


class BruteforcePrevention(Middleware):
    # if login_attempt == 1 and password == correct
    # return "Invalid username or password"
    pass


class SQLiConfuser(Middleware):
    pass


class HTAccessConfuser(Middleware):
    pass


class HeaderConfuser(Middleware):
    pass


class GZipMiddleware(Middleware):
    #from starlette.applications import Starlette
    #from starlette.middleware import Middleware
    #from starlette.middleware.gzip import GZipMiddleware
    
    #routes = ...
    
    #middleware = [
    #    Middleware(GZipMiddleware, minimum_size=1000)
    #]

    #app = Starlette(routes=routes, middleware=middleware)
    pass

class CORSMiddleware(Middleware):
    #from starlette.applications import Starlette
    #from starlette.middleware import Middleware
    #from starlette.middleware.cors import CORSMiddleware

    #middleware = [
    #    Middleware(CORSMiddleware, allow_origins=['*'])
    #]
    
    #app = Starlette(routes=routes, middleware=middleware)

    CORS = {
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": ("origin, content-type, accept, authorization, x-xsrf-token, x-request-id"),
    }
    pass

