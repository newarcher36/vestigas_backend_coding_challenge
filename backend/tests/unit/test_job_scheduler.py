from apscheduler.triggers.cron import CronTrigger

import backend.adapters.scheduling.job_scheduler as sched_mod
from backend.adapters.scheduling.job_scheduler import start_scheduler


class DummyScheduler:
    def __init__(self, timezone=None):
        self.timezone = timezone
        self.added = []
        self.started = False

    def add_job(self, func, trigger=None, kwargs=None, id=None, replace_existing=None):
        self.added.append({
            "func": func,
            "trigger": trigger,
            "kwargs": kwargs or {},
            "id": id,
            "replace_existing": replace_existing,
        })

    def start(self):
        self.started = True

    def shutdown(self, wait=False):
        pass


def test_start_scheduler_adds_cron_job(monkeypatch):
    # Patch BackgroundScheduler class to our dummy
    monkeypatch.setattr(sched_mod, "BackgroundScheduler", DummyScheduler)

    partner_urls = {"http://a", "http://b"}
    cron_trigger = CronTrigger.from_crontab("0 * * * *", timezone="UTC")
    scheduler = start_scheduler(partner_urls, cron_trigger)

    assert isinstance(scheduler, DummyScheduler)
    assert scheduler.started is True
    assert len(scheduler.added) == 1
    job = scheduler.added[0]
    assert isinstance(job["trigger"], CronTrigger)
    assert set(job["kwargs"].get("urls", [])) == {"http://a", "http://b"}
    assert job.get("id") == "partners-fetch"
