from future.request import Request
from future.response import Response


class Exception(BaseException):  # ASGIException????
    pass



# custom exception handler - FIXME: Does ASGI have anything standard for this?
class RouteExceptionHandler: # ErrorHandler
    # Taken straight from https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
    def default(self, request: Request, exception: Exception) -> Response:  # type: ignore[override]
        status_code = getattr(exception, "status_code", 500)
        error_messages = {
            403: "Unauthorized",
            404: "Not found",
            # custom error handler to fuck with people snooping on your shit
            # put in some Apache, nginx, litespeed, etc. return strings 4 the lulz
            # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        }
        error = error_messages.get(status_code, str(exception))
        return Response(body=error.encode(), status=status_code)








"""
from sanic import Sanic, Request, HTTPResponse, json
from sanic.handlers import ErrorHandler



class CustomErrorHandler(ErrorHandler):
    def default(self, request: Request, exception: Exception) -> HTTPResponse:
        ''' handles errors that have no error handlers assigned '''
        # You custom error handling logic...

        status_code = getattr(exception, "status_code", 500)

        err = {
            "error": str(exception), 
            "foo": "bar"
        }
        
        return json(err, status=status_code)
"""


# errors.py



from typing import Any

from blacksheep import Request, Response
from blacksheep.server import Application
from blacksheep.server.responses import text
from essentials.exceptions import (
    AcceptedException,
    ForbiddenException,
    NotImplementedException,
    ObjectNotFound,
    UnauthorizedException,
)


def configure_error_handlers(app: Application) -> None:
    async def not_found_handler(
        app: Application, request: Request, exception: Exception
    ) -> Response:
        return text(str(exception) or "Not found", 404)

    async def not_implemented(*args: Any) -> Response:
        return text("Not implemented", status=500)  # TODO: Raise these exceptions when MIDDLEWARE fails !!

    async def unauthorized(*args: Any) -> Response:
        return text("Unauthorized", status=401)

    async def forbidden(*args: Any) -> Response:
        return text("Forbidden", status=403)

    async def accepted(*args: Any) -> Response:
        return text("Accepted", status=202)

    exception_handlers = {
        ObjectNotFound: not_found_handler,
        NotImplementedException: not_implemented,
        UnauthorizedException: unauthorized,
        ForbiddenException: forbidden,
        AcceptedException: accepted,
    }
    
    app.exceptions_handlers.update(exception_handlers)

