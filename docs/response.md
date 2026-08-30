# Response
`future.response.Response` is a mutable builder. Controllers return `self.response.…(...)` (same instance Future injected).

## Builders
```python
self.response.json(data, status=200)
self.response.html(html)
self.response.text("ok")
self.response.empty(status=204)
self.response.redirect("/x")
self.response.file(body_bytes, content_type="application/octet-stream")
self.response.image(body_bytes, content_type="image/png")
self.response.stream([b"one", b"two"], content_type="text/plain")
self.response.set_cookie("a", "b", max_age=3600, domain="example.com")
self.response.delete_cookie("a")
```

Each builder sets status, body, and headers, then returns `self` so you can chain cookies:

```python
return self.response.json({"ok": True}).set_cookie("sid", token, httponly=True)
```

## Errors
```python
from future.exceptions import HTTPException
raise HTTPException("Not Found", 404)
```

## Legacy wrappers
`JSONResponse`, `PlainTextResponse`, etc. still exist as thin subclasses. Prefer `self.response.json(...)` on the injected instance.

## Streaming
`stream(chunks)` returns a `StreamingResponse`. That subclass owns the chunked ASGI send (`more_body`). `chunks` is an iterable or async iterable of `str` / `bytes` (a single `str` / `bytes` is one chunk). `json` / `text` / `file` still use `Response.__call__` (one body).

```python
return self.response.stream(["hello", " ", "world"], content_type="text/plain")
# or
from future.response import StreamingResponse
return StreamingResponse(["hello", " ", "world"], content_type="text/plain")
```

WebSocket sessions use `WebSocketResponse` — see [WebSockets](websockets.md).
