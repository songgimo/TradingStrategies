from abc import ABC, abstractmethod

from backend.domain.entities import MarketAnalysis
from backend.domain.value_objects import Symbol, StockMarketType
from backend.domain.reference_data import Interval
from backend.domain.entities import News
import pandas as pd # Pragmatic exception!
from typing import List


class MarketOutputPort(ABC):
    API_URL: str
    KEY: str
    SECRET: str

    @abstractmethod
    async def get_candle_history(self, target: Symbol, interval: Interval, count: int = 200) -> pd.DataFrame:
        ...

    @abstractmethod
    async def get_candles_history(self, targets: List[Symbol], interval: Interval, count: int = 1) -> pd.DataFrame:
        """
            1 day candle only supported.
        """
        ...

    @abstractmethod
    def get_all_symbols(self, market_type: StockMarketType):
        ...


class DatabaseOutputPort(ABC):
    @abstractmethod
    def put_ohlcv_to_database(self, data: pd.DataFrame):
        ...

    @abstractmethod
    def insert_news(self, news: List[News]):
        ...


class NewsCrawlerOutputPort(ABC):
    @abstractmethod
    async def fetch_news(self):
        ...


class LLMOutputPort(ABC):
    @abstractmethod
    async def analyze_market(self, news_contents: List[str]) -> MarketAnalysis:
        """
            Return MarketAnalysis
        """

