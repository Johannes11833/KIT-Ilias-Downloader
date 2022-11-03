import atexit
import datetime
from typing import Dict, Callable
from abc import ABC, abstractmethod
from dateutil import tz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class Task(ABC):
    function: Callable
    args: Dict

    def __init__(self, function: Callable, args: Dict | None = None) -> None:
        super().__init__()
        self.function = function
        self.args = args if args is not None else {}

    @abstractmethod
    def create_trigger() -> CronTrigger:
        return NotImplemented


class DailyTask(Task):
    target_time: str

    def __init__(
        self, target_time: str, function: Callable, args: Dict | None = None
    ) -> None:
        self.target_time = target_time
        super().__init__(function, args)

    def create_trigger(self) -> None:
        t = datetime.time.fromisoformat(self.target_time)
        CronTrigger(hour=t.hour, minute=t.minute, second=t.second)


class SingularTask(Task):
    target_time: datetime.datetime

    def __init__(
        self,
        target_time: datetime.datetime,
        function: Callable,
        args: Dict | None = None,
    ) -> None:
        self.target_time = target_time.astimezone(tz.tzlocal())
        super().__init__(function, args)

    def create_trigger(self) -> CronTrigger:
        return CronTrigger(
            year=self.target_time.year,
            month=self.target_time.month,
            day=self.target_time.day,
            hour=self.target_time.hour,
            minute=self.target_time.minute,
            second=self.target_time.second,
        )


class TimeScheduler:
    def __init__(self):
        self.task_list = []

    def start(self):
        scheduler = BackgroundScheduler()

        for task in self.task_list:
            trigger = task.create_trigger()
            scheduler.add_job(func=task.function, trigger=trigger)

        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    def add(self, task: Task):
        self.task_list.append(task)
