import logging
import asyncio

from apps.scheduler.celery_app import celery_app
from backend.application import app_services
from backend.domain.reference_data import StockMarketType, Interval
from backend.infrastructure.api.pykrx_api import PykrxAPI
from backend.infrastructure.crawler.google_rss import GoogleNews
from backend.infrastructure.db.database_api import SQLiteDatabase

from celery.exceptions import MaxRetriesExceededError


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_kospi_stock_ohlcv(self):
    """
        Task for collecting KOSPI stocks
        The business logic is in the use case.
    """
    logger.info(f"[Task {self.request.id}] Starting KOSPI data collection")

    try:
        service = app_services.CollectMarketDataService(
            PykrxAPI(),
            SQLiteDatabase(),
        )
        service.execute(StockMarketType.KOSPI)

        logger.info(f"[Task {self.request.id}] Successfully completed.")
    except Exception as ex:
        logger.error(f"[Task {self.request.id}] Failed to collect data: {ex}", exc_info=True)
        try:
            raise self.retry(exc=ex)

        except MaxRetriesExceededError:
            logger.critical(f"[Task {self.request.id}] MAX RETRIES EXCEEDED. Alerting Admin...")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_daily_news(self):
    """
    Task for collecting Daily News
    """
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Starting Daily News collection")

    try:
        service = app_services.CollectNewsService(
            GoogleNews(),
            SQLiteDatabase()
        )
        asyncio.run(service.execute())

        logger.info(f"[Task {task_id}] News collection completed successfully.")

    except Exception as ex:
        logger.error(f"[Task {task_id}] Failed to collect news: {ex}", exc_info=True)

        try:
            raise self.retry(exc=ex)
        except MaxRetriesExceededError:
            logger.critical(f"[Task {task_id}] MAX RETRIES EXCEEDED. Alerting Admin...")


if __name__ == '__main__':
    collect_kospi_stock_ohlcv()
