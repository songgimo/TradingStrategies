import logging
from apps.scheduler.celery_app import celery_app
from backend.application import app_services
from backend.domain.reference_data import StockMarketType, Interval
from backend.infrastructure.api.pykrx_api import PykrxAPI
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
        app_services.CollectMarketDataService(
            market_port=PykrxAPI(),
            database_port=SQLiteDatabase(),
            market=StockMarketType.KOSPI
        ).execute()

        logger.info(f"[Task {self.request.id}] Successfully completed.")
    except Exception as ex:
        logger.error(f"[Task {self.request.id}] Failed to collect data: {ex}", exc_info=True)
        try:
            raise self.retry(exc=ex)

        except MaxRetriesExceededError:
            logger.critical(f"[Task {self.request.id}] MAX RETRIES EXCEEDED. Alerting Admin...")


if __name__ == '__main__':
    collect_kospi_stock_ohlcv()
