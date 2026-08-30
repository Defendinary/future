from future.interfaces.ITask import ITask
from future.lifespan import Lifespan
from future.taskscheduler import CronScheduler, Unit


class FlagTask(ITask):
    name = "flag"
    interval = 1
    unit = Unit.SECONDS
    ran = False

    async def run(self) -> None:
        FlagTask.ran = True


class CountTask(ITask):
    name = "count"
    interval = 1
    unit = Unit.SECONDS
    count = 0

    async def run(self) -> None:
        CountTask.count += 1


async def test_lifespan_runs_startup_and_shutdown_tasks():
    FlagTask.ran = False
    startup = FlagTask()
    shutdown = CountTask()
    CountTask.count = 0
    lifespan = Lifespan(startup_tasks=[startup], shutdown_tasks=[shutdown])
    await lifespan.__aenter__()
    assert FlagTask.ran is True
    assert CountTask.count == 0
    await lifespan.__aexit__(None, None, None)
    assert CountTask.count == 1


def test_scheduler_skips_incomplete_tasks():
    scheduler = CronScheduler()

    class Incomplete(ITask):
        name = "incomplete"
        interval = None
        unit = None

        async def run(self) -> None:
            pass

    scheduler.add_task(Incomplete())
    assert scheduler.list_tasks() == []


def test_scheduler_add_list_remove():
    scheduler = CronScheduler()
    scheduler.add_task(CountTask())
    assert scheduler.list_tasks() == ["count"]
    assert scheduler.get_task("count") is not None
    assert scheduler.remove_task("count") is True
    assert scheduler.list_tasks() == []
    assert scheduler.remove_task("count") is False


async def test_scheduler_run_task_invokes_run():
    CountTask.count = 0
    scheduler = CronScheduler()
    scheduler.add_task(CountTask())
    await scheduler._run_task(scheduler.get_task("count"))
    assert CountTask.count == 1
    assert scheduler.get_task("count").last_run is not None
