from celery.schedules import crontab


BEAT_SCHEDULE = {
    "daily-market-update": {
        "task": "scheduler.tasks.collect_kospi_stock_ohlcv",
        "schedule": crontab(hour=20, minute=0),
    },
    "hourly-news-update": {
        "task": "apps.scheduler.tasks.collect_daily_news",
        "schedule": crontab(hours=8, minute=0),
    },
}
