import asyncio

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckSSHBannerTask(ITask):
    name = "check_ssh_banner"
    interval = 10
    unit = Unit.MINUTES

    def __init__(self, host: str = "localhost", port: int = 22) -> None:
        self.host = host
        self.port = port

    async def run(self) -> None:
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            banner = await reader.read(1024)
            log.info(f"SSH banner for {self.host}:{self.port}: {banner.decode(errors='ignore').strip()}")
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            log.error(f"SSH banner check failed for {self.host}:{self.port}: {e}")
