from typing import Optional

from future.interfaces.IMiddleware import IMiddleware
from future.response import Response


class CSRFMiddleware(IMiddleware):
    name = "CSRFMiddleware"
    cookie_name = "csrf_token"
    header_name = "x-csrf-token"
    safe_methods = {"GET", "HEAD", "OPTIONS"}

    async def before(self) -> Optional[Response]:
        import secrets
        token = self.request.cookies.get(self.cookie_name)
        if not token:
            token = secrets.token_urlsafe(32)
            self.request.context["csrf_token_new"] = token
        self.request.context["csrf_token"] = token
        if self.request.method in self.safe_methods:
            return None
        provided = self.request.headers.get(self.header_name) or self.request.headers.get("x-xsrf-token")
        if not provided:
            form = await self.request.form()
            value = form.get("csrf_token")
            provided = value if isinstance(value, str) else None
        if not provided or not secrets.compare_digest(str(provided), str(token)):
            return self.response.json({"error": "CSRF token missing or invalid", "status_code": 403}, status=403)
        return None

    async def after(self) -> Optional[Response]:
        token = self.request.context.get("csrf_token_new") or self.request.context.get("csrf_token")
        if token:
            self.response.set_cookie(self.cookie_name, token, httponly=False, samesite="Strict", secure=(self.request.scheme == "https"))
        return None
