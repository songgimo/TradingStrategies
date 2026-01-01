import logging
from apps.scheduler.celery_app import celery_app
from backend.application import app_services
from backend.domain.reference_data import StockMarketType, Interval
from backend.infrastructure.api.pykrx_api import PykrxAPI

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_kospi_stock_ohlcv(self):
    """
        Task for collecting KOSPI stocks
        The business logic is in the use case.
    """
    logger.info(f"[Task {self.request.id}] Starting KOSPI data collection")

    try:
        market_port = PykrxAPI()

        market_data_service = app_services.MarketDataService(
            market_port,
        )

        return market_data_service.collecting_ohlcv(
            interval=Interval.DAY,
            count=200
        )

    except:
        ...
