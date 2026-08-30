import subprocess

from future.interfaces.ITask import ITask
from future.logger import log
from future.taskscheduler import Unit


class CheckSystemUptimeTask(ITask):
    name = "check_system_uptime"
    interval = 15
    unit = Unit.MINUTES

    async def run(self) -> None:
        try:
            result = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5.0)
            if result.returncode == 0:
                log.info(f"System uptime: {result.stdout.strip()}")
            else:
                log.error(f"Uptime command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            log.error("Uptime command timed out")
        except Exception as e:
            log.error(f"Error checking system uptime: {e}")
