from celery.schedules import crontab


BEAT_SCHEDULE = {
    "daily-market-update": {
        "task": "scheduler.tasks.update_daily_data",
        "schedule": crontab(hour=20, minute=0),
    },
}
