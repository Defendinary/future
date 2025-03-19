import httpx
from future.application import Future


class FutureTestClient:
    def __init__(self, app: Future):
        self.app = app
        self.transport = httpx.ASGITransport(app=self.app)
        self.client = httpx.AsyncClient(transport=self.transport)  # base_url="http://example.com") # TODO: We dont need base_url any longer since we have decided to use Host header instead.

    async def get(self, path: str):
        response = await self.client.get(path)
        return response

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)
