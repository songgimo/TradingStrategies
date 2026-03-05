from celery.schedules import crontab


BEAT_SCHEDULE = {
    "daily-market-update": {
        "task": "scheduler.tasks.collect_kospi_stock_ohlcv",
        "schedule": crontab(hour=20, minute=0),
    },
    "hourly-news-update": {
        "task": "apps.scheduler.tasks.collect_daily_news",
        "schedule": crontab(hour=8, minute=0),
    },
    "daily-strategy-generation": {
        "task": "src.apps.scheduler.worker_task.generate_trade_strategies_task",
        "schedule": crontab(hour=21, minute=0),
    },
}

