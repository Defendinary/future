from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class ScopeValidationMiddleware(IMiddleware):
    name = "scopeValidation"
    priority = 10

    async def before(self) -> Optional[Response]:
        if self.request.path in ["/health", "/ping"]:
            return None
        route = getattr(self.request, "route", None)
        if not route:
            return None
        required_scopes = getattr(route, "scopes", [])
        if not required_scopes:
            return None
        user_id = self.request.context.get("user_id")
        if not user_id:
            return self.response.text("Unauthorized - no user ID found", status=401)
        user_scopes = self.request.context.get("scopes") or []
        for required_scope in required_scopes:
            if required_scope not in user_scopes:
                return self.response.text("Insufficient permissions", status=403)
        return None
