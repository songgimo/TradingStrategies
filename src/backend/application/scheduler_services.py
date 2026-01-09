import logging
import json
from dataclasses import dataclass

from src.backend.application.ports.output import MarketOutputPort, DatabaseOutputPort, NewsCrawlerOutputPort
from src.backend.domain.reference_data import Interval, StockMarketType
from src.backend.domain.value_objects import Symbol
from src.config.config import STATIC_FOLDER_PATH

logger = logging.getLogger(__name__)


@dataclass
class CollectMarketDataService:
    """
        Use case for collecting market data.

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
        print(data)
        # self.database_port.get_ohlcv_data()

        # self.database_port.put_ohlcv_to_database(result)


@dataclass
class CollectNewsService:
    news_crawler_port: NewsCrawlerOutputPort
    database_port: DatabaseOutputPort

    async def execute(self):
        news = await self.news_crawler_port.fetch_news()
        self.database_port.put_news(news)
