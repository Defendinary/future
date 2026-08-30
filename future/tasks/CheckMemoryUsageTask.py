import psutil

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckMemoryUsageTask(ITask):
    name = "check_memory_usage"
    interval = 5
    unit = Unit.MINUTES

    async def run(self) -> None:
        try:
            memory = psutil.virtual_memory()
            log.info(f"Memory usage: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        except ImportError:
            log.warning("psutil not available, skipping memory check")
        except Exception as e:
            log.error(f"Error checking memory usage: {e}")
