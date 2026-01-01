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
    def get_candles_history(self, targets: List[Symbol], interval: Interval, count: int = 200) -> pd.DataFrame:
        ...
