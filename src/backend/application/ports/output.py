import datetime
from abc import ABC, abstractmethod

from src.backend.domain.entities import MarketAnalysis
from src.backend.domain.value_objects import Symbol
from src.backend.domain.reference_data import Interval, StockMarketType
from src.backend.domain.entities import News
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
    def put_news(self, news: List[News]):
        ...

    @abstractmethod
    def get_news_by_date(self, target_date: datetime.date) -> List[News]:
        """
            Query news with target date.
        """

    @abstractmethod
    def save_market_analysis(self, analysis: MarketAnalysis):
        """
            save the results of market analysis.
        """


class NewsCrawlerOutputPort(ABC):
    @abstractmethod
    async def fetch_news(self):
        ...


class LLMOutputPort(ABC):
    @abstractmethod
    async def analyze_market(self, news_contents: List[News]) -> MarketAnalysis:
        """
            Return MarketAnalysis
        """

