from abc import ABC, abstractmethod
from backend.domain.value_objects import Ticker, Stock, DataOHLCV, Symbol
from backend.domain.reference_data import StockMarketType, CryptoMarketType
import typing
import pandas as pd # Pragmatic exception!
from datetime import date


class StockMarketOutputPort(ABC):
    @abstractmethod
    def get_candle_history(self, target: Symbol, start: date, end: date) -> pd.DataFrame:
        ...


class CryptoMarketOutputPort(ABC):
    API_URL: str
    KEY: str
    SECRET: str

    @abstractmethod
    def get_candle_history(self, symbol: Symbol) -> pd.DataFrame:
        ...
