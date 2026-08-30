import socket

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckDNSTask(ITask):
    name = "check_dns"
    interval = 5
    unit = Unit.MINUTES

    def __init__(self, domain: str = "example.com") -> None:
        self.domain = domain

    async def run(self) -> None:
        try:
            ip = socket.gethostbyname(self.domain)
            log.info(f"DNS: {self.domain} -> {ip}")
        except socket.gaierror as e:
            log.error(f"DNS lookup failed for {self.domain}: {e}")
