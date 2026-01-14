import logging
import json
from dataclasses import dataclass

from src.backend.application.ports.output import MarketOutputPort, DatabaseOutputPort, NewsCrawlerOutputPort, \
    LLMOutputPort
from src.backend.domain.reference_data import Interval, StockMarketType
from src.backend.domain.value_objects import Symbol
from src.config.config import STATIC_FOLDER_PATH

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

    async def execute(self, market: StockMarketType, interval: Interval = Interval.DAY, count: int = 1):
        if market in [StockMarketType.KOSPI]:
            with open(STATIC_FOLDER_PATH / "kospi_200_codes.json", "r") as f:
                codes = json.loads(f.read())
        else:
            raise ValueError(
                f"Unsupported market type: {market}"
            )
        symbols = [Symbol(code) for code in codes]
        data = await self.market_port.get_candles_history(symbols, interval, count)
        self.database_port.put_ohlcv_to_database(data)


@dataclass
class CollectNewsService:
    news_crawler_port: NewsCrawlerOutputPort
    database_port: DatabaseOutputPort
    llm_port: LLMOutputPort

    async def execute(self):
        news_list = await self.news_crawler_port.fetch_news()

        if not news_list:
            logger.warning("No news collected.")
            return

        logger.info(f"Saving {len(news_list)} news items to Database..")
        self.database_port.put_news(news_list)

        logger.info("Analyzing market with LLM...")
        market_analysis = await self.llm_port.analyze_market(news_list)

        logger.info(f"Saving analysis result: {market_analysis.summary}")
        self.database_port.save_market_analysis(market_analysis)


if __name__ == '__main__':
    from src.backend.infrastructure.crawler.mk_rss import MKNews
    from src.backend.infrastructure.llm.langchain_adapter import LangChainAdapter
    from src.backend.infrastructure.db.database_api import SQLiteDatabase
    import asyncio

    service = CollectNewsService(
        MKNews(),
        SQLiteDatabase(),
        LangChainAdapter()
    )
    asyncio.run(service.execute())
