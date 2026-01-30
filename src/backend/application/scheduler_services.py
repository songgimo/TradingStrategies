import logging
import datetime
from dataclasses import dataclass

from src.backend.application.ports.output import MarketOutputPort, DatabaseOutputPort, NewsCrawlerOutputPort, \
    LLMOutputPort
from src.backend.domain.reference_data import Interval, StockMarketType
from src.backend.domain.value_objects import Symbol

from typing import List

logger = logging.getLogger(__name__)


@dataclass
class CollectMarketDataService:
    """
        Use case for collecting market data.
            Map-Reduce패턴
        Orchestrates:
        - Fetching OHLCV data from APIs
        - Storing data in database.
        - Error handling and retry logic
    """
    market_port: MarketOutputPort
    database_port: DatabaseOutputPort

    async def execute(self, symbols: List[Symbol], interval: Interval = Interval.DAY, count: int = 1):
        data = await self.market_port.get_candles_history(symbols, interval, count)
        self.database_port.put_ohlcv_to_database(data)


@dataclass
class CollectNewsService:
    news_crawler_port: NewsCrawlerOutputPort
    database_port: DatabaseOutputPort

    async def execute(self):
        news_list = await self.news_crawler_port.fetch_news()

        if not news_list:
            logger.warning("No news collected.")
            return

        logger.info(f"Saving {len(news_list)} news items to Database..")
        self.database_port.put_news(news_list)

        return len(news_list)


@dataclass
class NewsAnalysisService:
    database_port: DatabaseOutputPort
    llm_port: LLMOutputPort

    async def execute(self):
        today = datetime.datetime.now().date()
        news_list = self.database_port.get_news_by_date(today)
        if not news_list:
            return "No news to analyze"

        analysis = await self.llm_port.analyze_market(news_list)
        self.database_port.save_market_analysis(analysis)
        return analysis.summary
