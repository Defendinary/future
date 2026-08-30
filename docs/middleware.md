# Middleware
`future.interfaces.IMiddleware` runs around controller actions. Same `request` / `response` injection as controllers.

```python
from typing import Optional
from future.interfaces.IMiddleware import IMiddleware
from future.response import Response
from future.exceptions import HTTPException

class AuthMiddleware(IMiddleware):
    async def before(self) -> Optional[Response]:
        if not self.request.headers.get("authorization"):
            raise HTTPException("unauthorized", 401)
        return None

    async def after(self) -> Optional[Response]:
        return None
```

Attach on a group or route: `middlewares=[AuthMiddleware]`.

- `before` runs outer → inner → controller
- `after` runs in reverse
- Return a `Response` from `before` to short-circuit (skip the controller)

## Built-ins
Import from the class file: CORS, GZip, CSRF, RateLimit, Session, ScopeValidation. Confuser classes exist but are unfinished — see [Gaps](gaps.md).

`ScopeValidationMiddleware` reads `request.route.scopes` and `request.context["user_id"]` / `request.context["scopes"]` (set by your auth middleware). Missing `user_id` → 401; missing required scope → 403. Routes with no `scopes=` are skipped.

## Sessions
```python
from future.middleware.SessionMiddleware import SessionMiddleware
from future.routing import RouteGroup, Get, Post

RouteGroup(
    name="Auth",
    middlewares=[SessionMiddleware],
    routes=[
        Post("/login", AuthController.login, "login"),
        Get("/me", AuthController.me, "me"),
    ],
)
```

Then `self.request.session["user"] = "alice"`.
