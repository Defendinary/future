import httpx
from future.application import Future


class FutureTestClient:
    def __init__(self, app: Future):
        self.app = app
        self.transport = httpx.ASGITransport(app=self.app)
        self.client = httpx.AsyncClient(transport=self.transport)

    async def get(self, path: str, headers: dict | None = None):
        response = await self.client.get(path, headers=headers)
        return response

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)
