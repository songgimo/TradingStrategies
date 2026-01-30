import logging

from src.apps.scheduler.celery_app import celery_app
from src.backend.application import scheduler_services
from src.backend.application.scheduler_services import NewsAnalysisService
from src.backend.domain.reference_data import StockMarketType, NewsSourceType
from src.backend.domain.entities import Symbol
from src.backend.infrastructure.api.factory import MarketAPIFactory
from src.backend.infrastructure.crawler.factory import NewsCrawlerFactory

from src.backend.infrastructure.llm.langchain_adapter import LangChainAdapter
from src.backend.infrastructure.db.database_api import SQLiteDatabase


logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    reject_on_worker_lost=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=3600,
    retry_jitter=True,
    rate_limit="30/m",
)
def collect_stock_data_chunk(self, market_type: StockMarketType, code: str):
    """
        Task for collecting KOSPI stocks
        The business logic is in the use case.
    """
    logger.info(f"[Task {self.request.id}] Starting KOSPI data collection")
    market_port = MarketAPIFactory.get_port(market_type)
    service = scheduler_services.CollectMarketDataService(
        market_port,
        SQLiteDatabase()
    )

    symbols = Symbol(code)
    service.execute(symbols)
    logger.info(f"[Task {self.request.id}] Successfully completed.")

    return f"KOSPI collection success: {self.request.id}"


@celery_app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=60,
    rate_limit="5/m",
    queue="news_queue",
)
def collect_daily_news(self, source: NewsSourceType):
    """
    Task for collecting Daily News
    """
    logger.info(f"[Task {self.request.id}] Starting Daily News collection")
    crawler_port = NewsCrawlerFactory.get_port(source)

    service = scheduler_services.CollectNewsService(
        crawler_port,
        SQLiteDatabase(),
    )
    service.execute()

    logger.info(f"[Task {self.request.id}] News collection completed successfully.")


@celery_app.task(queue="news_queue")
def analyze_market_news_task(results):
    service = NewsAnalysisService(SQLiteDatabase(), LangChainAdapter())

    summary = service.execute()
    return f"Market Analysis Completed: {summary}"