import httpx

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckHttpStatusTask(ITask):
    name = "check_http_status"
    interval = 5
    unit = Unit.MINUTES

    def __init__(self, url: str = "https://httpbin.org/status/200") -> None:
        self.url = url

    async def run(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url)
                log.info(f"HTTP: {self.url} -> {response.status_code}")
        except Exception as e:
            log.error(f"HTTP check failed for {self.url}: {e}")
