from datetime import datetime

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class SyncTaskExample(ITask):
    name = "sync_task_example"
    interval = 1
    unit = Unit.HOURS

    async def run(self) -> None:
        log.info(f"Running sync task at {datetime.now()}")
