# Lifespan
`future.lifespan.Lifespan` is the ASGI lifespan hook required by `Future`. You pass in lists of [Tasks](tasks.md) to run at startup, on a schedule while the app is up, and at shutdown.

```python
from future.lifespan import Lifespan
from future.interfaces.ITask import ITask
from future.taskscheduler import Unit
from future.application import Future
from app.tasks.ScrapeTask import ScrapeTask


class BootTask(ITask):
    name = "boot"

    async def run(self) -> None:
        ...


lifespan = Lifespan(
    startup_tasks=[BootTask()],
    shutdown_tasks=[],
    cron_tasks=[ScrapeTask()],
)
app = Future(lifespan=lifespan, config=config)
```

## Slots
| List | When |
|------|------|
| `startup_tasks` | Once on ASGI startup, in order |
| `cron_tasks` | Registered with the interval scheduler after startup |
| `shutdown_tasks` | Once on ASGI shutdown, after the scheduler stops |

Empty lists are fine:

```python
Lifespan(startup_tasks=[], shutdown_tasks=[], cron_tasks=[])
```

## Lifecycle
1. Run `startup_tasks` (`await task.run()`).
2. Start `CronScheduler` and register `cron_tasks`.
3. App serves traffic; interval tasks fire in the background.
4. On shutdown: stop the scheduler, then run `shutdown_tasks`.

How to build an `ITask` (name, interval, jitter, …): see [Tasks](tasks.md).
