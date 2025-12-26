from celery import Celery
from config.config import settings


celery_app = Celery(
    "scheduler",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend_url,
    include=["apps.scheduler.tasks"]
)

celery_app.conf.update(
    timezone="Asia/Seoul",
    enable_utc=False,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

from apps.scheduler.beat_schedule import BEAT_SCHEDULE
celery_app.conf.beat_schedule = BEAT_SCHEDULE
