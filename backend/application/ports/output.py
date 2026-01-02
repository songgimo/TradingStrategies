from abc import ABC, abstractmethod
from backend.domain.value_objects import Symbol, StockMarketType
from backend.domain.reference_data import Interval
import pandas as pd # Pragmatic exception!
from typing import List


class MarketOutputPort(ABC):
    API_URL: str
    KEY: str
    SECRET: str

    @abstractmethod
    def get_candle_history(self, target: Symbol, interval: Interval, count: int = 200) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_candles_last_day_history(self, targets: List[Symbol], market: StockMarketType) -> pd.DataFrame:
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
