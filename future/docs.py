
# API Spec generated based on settings
API_SPEC = {
    "openapi": "1.0.0.",
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    }
}





"""
This module contains OpenAPI Documentation definition for the API.

It exposes a docs object that can be used to decorate request handlers with additional
information, used to generate OpenAPI documentation.
"""
from blacksheep import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info

from app.docs.binders import set_binders_docs
from app.settings import Settings


def configure_docs(app: Application, settings: Settings):
    docs = OpenAPIHandler(
        info=Info(title=settings.info.title, version=settings.info.version),
        anonymous_access=True,
    )

    # include only endpoints whose path starts with "/api/"
    docs.include = lambda path, _: path.startswith("/api/")

    set_binders_docs(docs)

    docs.bind_app(app)


"""
This module contains definitions of custom binders, used to bind request input
parameters into instances of objects, injected to request handlers.
"""
from blacksheep import FromHeader, Request
from blacksheep.server.bindings import Binder

from domain.common import PageOptions


class IfNoneMatchHeader(FromHeader[str | None]):
    name = "If-None-Match"


class PageOptionsBinder(Binder):
    """
    Binds common pagination options for all endpoints implementing pagination of
    results. Collects and validates optional the following query parameters:

    - page, for page number
    - limit, for results per page
    - continuation_id, the last numeric ID that was read
    """

    handle = PageOptions

    async def get_value(self, request: Request) -> PageOptions:
        page = request.query.get("page")
        limit = request.query.get("limit")
        continuation_id = request.query.get("continuation_id")
        
        if page is None:
            page = 1
        else:
            page = page[0]
            
        if limit is None:
            limit = 100
        else:
            limit = limit[0]
            
        if continuation_id is not None:
            continuation_id = int(continuation_id[0])
            
        return PageOptions(page=page, limit=limit, continuation_id=continuation_id)



"""
This module configures OpenAPI Documentation for custom binders.
"""
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Parameter, ParameterLocation, Schema, ValueFormat, ValueType

from app.binders import PageOptionsBinder


def set_binders_docs(docs: OpenAPIHandler):
    """
    This function configures OpenAPI Documentation for custom application binders.
    """
    docs.set_binder_docs(
        PageOptionsBinder,
        [
            Parameter(
                "page",
                ParameterLocation.QUERY,
                description="Page number.",
                schema=Schema(minimum=0, format=ValueFormat.INT64, default=1),
            ),
            Parameter(
                "limit",
                ParameterLocation.QUERY,
                description="Number of results per page.",
                schema=Schema(
                    minimum=0, maximum=1000, format=ValueFormat.INT32, default=100
                ),
            ),
            Parameter(
                "continuation_id",
                ParameterLocation.QUERY,
                description=(
                    "Optional, ID of the last item that was retrieved. "
                    "If provided, enables faster pagination."
                ),
                schema=Schema(format=ValueFormat.INT64, default=None),
            ),
            Parameter(
                "order",
                ParameterLocation.QUERY,
                description=("Optional sort order (asc / desc) - default asc."),
                schema=Schema(ValueType.STRING, default=None),
            ),
        ],
    )





