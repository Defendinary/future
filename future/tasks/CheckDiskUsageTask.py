import shutil

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckDiskUsageTask(ITask):
    name = "check_disk_usage"
    interval = 30
    unit = Unit.MINUTES

    def __init__(self, path: str = "/") -> None:
        self.path = path

    async def run(self) -> None:
        try:
            total, used, _ = shutil.disk_usage(self.path)
            used_percent = (used / total) * 100
            log.info(f"Disk usage for {self.path}: {used_percent:.1f}% used ({used // (1024**3)}GB / {total // (1024**3)}GB)")
        except Exception as e:
            log.error(f"Error checking disk usage for {self.path}: {e}")
