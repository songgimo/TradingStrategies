import logging
from dataclasses import dataclass

from backend.application.ports.output import MarketOutputPort, DatabaseOutputPort, NewsCrawlerOutputPort
from backend.domain.reference_data import Interval, StockMarketType

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

    def execute(self, market: StockMarketType):
        if market in [StockMarketType.KOSPI, StockMarketType.KOSDAQ]:
            history_data = self.market_port.get_candles_last_day_history(
                [],
                market
            )

        else:
            raise ValueError(
                f"Unsupported market type: {market}"
            )

        self.database_port.put_ohlcv_to_database(history_data)


@dataclass
class CollectNewsService:
    news_crawler_port: NewsCrawlerOutputPort
    database_port: DatabaseOutputPort

    async def execute(self):
        news = await self.news_crawler_port.fetch_news()
        self.database_port.insert_news(news)
