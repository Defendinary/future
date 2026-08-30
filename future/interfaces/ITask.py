from datetime import datetime
from typing import Optional

from future.interfacing import Interface
from future.taskscheduler import Unit


class ITask(Interface):
    name: str = ""
    interval: Optional[int] = None
    unit: Optional[Unit] = None
    start_time: Optional[datetime] = None
    jitter: Optional[float] = None

    async def run(self) -> None:
        raise NotImplementedError
