from abc import ABC, abstractmethod
from backend.domain.value_objects import Ticker, Stock, DataOHLCV, Symbol
from backend.domain.reference_data import Interval
import typing
import pandas as pd # Pragmatic exception!
from datetime import date


class MarketOutputPort(ABC):
    API_URL: str
    KEY: str
    SECRET: str

    @abstractmethod
    def get_candle_history(self, target: Symbol, interval: Interval, count: int = 200) -> pd.DataFrame:
        ...
