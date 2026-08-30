from datetime import datetime

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class DailyBackupTask(ITask):
    name = "daily_backup"
    interval = 1
    unit = Unit.DAYS

    async def run(self) -> None:
        log.info(f"Running daily backup at {datetime.now()}")
        # TODO: Implement actual backup logic
        # Example: backup database, files, etc.
