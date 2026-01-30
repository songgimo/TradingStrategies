import logging
import json

from celery import chord

from src.apps.scheduler.celery_app import celery_app
from src.apps.scheduler.worker_task import collect_stock_data_chunk, collect_daily_news, analyze_market_news_task
from src.backend.domain.reference_data import StockMarketType, NewsSourceType
from celery import group
from src.config.config import STATIC_FOLDER_PATH


logger = logging.getLogger(__name__)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _load_codes(stock_file_path: str):
    with open(STATIC_FOLDER_PATH / stock_file_path, "r") as f:
        return json.loads(f.read())


@celery_app.task(bind=True, queue="market_queue")
def master_collect_stocks():
    kospi_codes = _load_codes("kospi_200_codes.json")
    kospi_groups = group(
        collect_stock_data_chunk.s(StockMarketType.KOSPI, chunk).set(queue="kospi_queue")
        for chunk in chunks(kospi_codes, 20)
    )
    kospi_groups.apply_async()

    nasdaq_codes = _load_codes("nasdaq_codes.json")
    nasdaq_groups = group(
        collect_stock_data_chunk.s(StockMarketType.KOSDAQ, chunk).set(queue="nasdaq_queue")
        for chunk in chunks(nasdaq_codes, 50)
    )
    nasdaq_groups.apply_async()


@celery_app.task(queue="news_queue")
def master_collect_news():
    """
    1. 각 뉴스 소스별 수집 태스크를 생성 (Group)
    2. 모든 수집이 완료되면 분석 태스크를 실행 (Callback/Chord)
    """
    sources = [NewsSourceType.MK_STOCK, NewsSourceType.HK_FINANCE]

    header = [collect_daily_news.s(source) for source in sources]

    callback = analyze_market_news_task.s()

    return chord(header)(callback)